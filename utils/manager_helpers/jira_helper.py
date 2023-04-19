import datetime
import json
import logging
import re
import time

import jira.exceptions
import jira.resources
import requests
import requests as r
from jira import JIRA, Issue

from utils.constants import JIRA_RELEASE_PATTERN, HTTPS_CONFLUENCE_URL, HTTPS_JIRA_URL
from utils.jira import JIRA_PASSWORD, JIRA_USER
from utils.manager_helpers.constants import (
    AUTOTESTS_DESCRIPTION,
    CREATE_TECH_DOCUMENTS,
    DEMO_DESCRIPTION,
    LOAD_DESCRIPTION,
    MANUAL_DESCRIPTION,
    QA_VERIFICATION_DESCRIPTION,
    Labels,
    Project,
    Projects,
    Summaries,
    TaskType,
)
from utils.manager_helpers.issue_types import SUBTASK_RELEASE_TYPES, IssueTypes
from utils.manager_helpers.users import Engineer, Roles, Users


class JiraIssueStatus:
    BACKLOG = "Backlog"
    PBR = "PBR"
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    READY_FOR_DEVELOPMENT = "Ready for Development"
    DEVELOPMENT = "Development"
    REVIEW = "Review"
    READY_FOR_TEST = "Ready for Test"
    TESTING = "Testing"
    READY_TO_CHECK = "Ready to Check"
    READY_TO_INSTALL = "Ready to Install"
    CLOSED = "Closed"


class JiraIssueTransitionStatus:
    name: str
    jira_id: str

    def __init__(self, name, jira_id):
        self.name = name
        self.jira_id = jira_id


class JiraIssueTransitionStatuses:
    TO_PBR: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="To PBR", jira_id="231")
    READY_TO_WORK: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Ready to Work", jira_id="171")
    START_WORK: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Start Work", jira_id="71")
    TO_DEVELOPMENT: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="To Development", jira_id="331")
    TO_REVIEW: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="To Review", jira_id="351")
    START_DEVELOPMENT: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Start Development", jira_id="341")
    TO_TEST: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="To Test", jira_id="361")
    START_TESTING: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Start Testing", jira_id="271")
    FINISH_TESTING: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Finish Testing", jira_id="281")
    APPROVE: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Approve", jira_id="41")
    CLOSE: JiraIssueTransitionStatus = JiraIssueTransitionStatus(name="Close", jira_id="11")


class JiraHelper:
    def __init__(
            self, user=JIRA_USER, password=JIRA_PASSWORD, project=Projects.MYPROJECT1, server=HTTPS_JIRA_URL,
            verify=False
    ):
        self.basic_auth = (user, password)
        some_id = "123"
        self.headers = {"Accept": "application/json", "Content-Type": "application/json", "some_id": some_id}
        self.server = server
        self.verify = verify
        if isinstance(project, str):
            self.project = getattr(Projects, project.upper())
        elif isinstance(project, Project):
            self.project = project
        # todo: fix jira_options !
        self.jira_options = {"server": self.server, "verify": self.verify, "headers": {"some_id": some_id}}
        # todo: fix me self._jira = JIRA switch ON!
        self._jira = JIRA(options=self.jira_options, basic_auth=self.basic_auth)
        self.SUBTASK_RELEASE_TYPES = self.get_subtask_release_types()

    def get_subtask_release_types(self):
        if self.project == Projects.MYPROJECT1:
            sub_task_release_types = SUBTASK_RELEASE_TYPES
        else:
            sub_task_release_types = [
                TaskType.DevOps.deploy_stage,
                TaskType.QA.release_verification,
                TaskType.DevOps.deploy_prod,
            ]
        return sub_task_release_types

    def is_jira_key_exist(self, parent_task_key: str) -> bool:
        try:
            self._jira.issue(parent_task_key)
        except Exception as e:
            print(e.args[0])
            return False
        return True

    def get_issue(self, task_key) -> Issue | None:
        if not self.is_jira_key_exist(task_key):
            return None
        return self._jira.issue(task_key)

    def get_issue_status(self, task_key) -> str:
        jql_str = f"key={task_key}"
        task = self._jira.search_issues(jql_str=jql_str, fields=["status"])[0]
        return task.fields.status.name

    def get_all_story_keys(self, project=Projects.MYPROJECT1, version: str = "0.13"):
        jql_str = f"project = {project} AND fixVersion = {version} and type = Story and labels in (backend)"
        return [_.key for _ in self.get_issues_jql(jql_str=jql_str, fields="key")]

    def get_issues_jql(self, jql_str, fields=None, maxResults=6, startAt=0):
        return self._jira.search_issues(jql_str=jql_str, fields=fields, maxResults=maxResults, startAt=startAt)

    def generate_subtask_summary(self, parent_task, sub_task_type):
        parent_issue = self._jira.issue(id=parent_task)
        return self.generate_summary(sub_task_type) + " " + parent_issue.fields.summary

    def is_sub_task_exists(self, parent_task, sub_task_type=None) -> bool:
        issue = self._jira.issue(id=parent_task)
        # sub_task_summary = self.generate_subtask_summary(parent_task, sub_task_type)
        sub_task_summary = self.generate_summary(sub_task_type)
        try:
            for sub_task in issue.fields.subtasks:
                if sub_task_summary in sub_task.fields.summary:
                    return True
        except Exception as e:
            print(e.args[0])
        return False

    @staticmethod
    def generate_summary(task_type) -> str:
        return Summaries.all.get(task_type)

    @staticmethod
    def get_current_quarter() -> str:
        today = datetime.date.today()
        current_quarter = (today.month - 1) // 3 + 1
        current_year = today.year
        quarter_fix_version = str(current_year)[2:] + "Q" + str(current_quarter)
        return quarter_fix_version

    def generate_subtask(
            self,
            parent_task_key: str,
            task_type: TaskType,
            project=None,
            assignee=None,
            issue_type_id=None,
            task_name=None,
    ) -> dict:
        summary, description, labels = "", "", []

        if issue_type_id is None:
            issue_type_id = self.get_issue_type_id(task_type)
        if assignee is None:
            assignee = self.get_assignee(task_type)

        if project is None:
            project = self.project

        if isinstance(parent_task_key, jira.resources.Issue):
            parent_task_key = parent_task_key.key
        elif not isinstance(parent_task_key, str):
            assert isinstance(issue_type_id, str)

        if not self.is_jira_key_exist(parent_task_key):
            raise NameError(f"Такой задачи в Jira нет {parent_task_key}")

        parent_issue = self._jira.issue(parent_task_key)

        summary = self.get_summary(parent_issue=parent_issue, task_name=task_name, task_type=task_type)

        fix_versions = self.get_or_create_fix_versions(parent_task_key)

        assignee, description, labels, summary = self.get_subtask_attributes(
            assignee, description, labels, parent_issue, summary, task_type
        )

        if isinstance(project, Project):
            project_key = project.key
        elif isinstance(project, str):
            project_key = project
        else:
            raise NameError(f"ERROR: Надо разобраться какой {project} используем.")

        if project_key in Projects.any:
            if isinstance(assignee, Engineer):
                assignee = assignee.name
            elif not isinstance(assignee, str):
                raise NameError("Укажите правильный тип исполнителя")
            assert assignee in [
                user.name for user in getattr(Users, str(getattr(Projects, project_key)).lower())
            ], f"{assignee} нет в проекте {project}"

        return {
            "project": project_key,
            "parent": {"key": parent_task_key},
            "summary": summary,
            "description": description,
            "labels": labels,
            "assignee": {"name": assignee},
            "issuetype": {"id": issue_type_id},
            "fixVersions": fix_versions,
        }

    def get_subtask_attributes(self, assignee, description, labels: list, parent_issue, summary, task_type):
        if task_type == TaskType.QA.verification:
            description = QA_VERIFICATION_DESCRIPTION
            labels = [Labels.qc, Labels.verification]
        elif task_type == TaskType.QA.auto:
            description = AUTOTESTS_DESCRIPTION
            labels = [Labels.aqa]
        elif task_type == TaskType.QA.manual:
            description = MANUAL_DESCRIPTION
            labels = [Labels.qa, Labels.testcase]
        elif task_type == TaskType.QA.demo:
            description = DEMO_DESCRIPTION
            labels = [Labels.qa]
        elif task_type == TaskType.QA.load:
            description = LOAD_DESCRIPTION
            labels = [Labels.lqa]
        elif task_type == TaskType.TechDoc.techdoc:
            summary = "Создать/обновить документацию: " + parent_issue.fields.summary
            description = CREATE_TECH_DOCUMENTS
            labels = [Labels.techdoc]
        elif task_type == TaskType.Any.education:
            summary = "Пройти обучение: " + parent_issue.fields.summary
            description = CREATE_TECH_DOCUMENTS
            labels = [Labels.meetings]
        elif task_type in [prop for prop in dir(TaskType.DevOps) if not prop.startswith("_")]:
            assignee = [
                user for user in getattr(Users, self.project.key.lower()) if user.qualification == Roles.devops
            ][0]
            description = summary
        elif task_type == TaskType.Pm.check_tasks:
            assignee = [user for user in getattr(Users, self.project.key.lower()) if user.qualification == Roles.pm][0]
            description = summary
        elif task_type == TaskType.TechDoc.release_notes:
            assignee = Users.techwriter_login
            description = summary

        labels += self.get_smart_labels(assignee)
        return assignee, description, labels, summary

    def get_smart_labels(self, assignee):
        if isinstance(assignee, str):
            return [getattr(Users, assignee).qualification]
        elif isinstance(assignee, Engineer):
            return [getattr(Users, assignee.name).qualification]
        else:
            raise NameError("Для умных меток можно использовать только str, User")

    def get_or_create_fix_versions(self, parent_task_key):
        if self.project == Projects.MYPROJECT1:
            fix_version_name = self.get_current_quarter()
            version = self._jira.get_project_version_by_name(project=self.project.key, version_name=fix_version_name)
            if not version:
                fix_version = self._jira.create_version(name=fix_version_name, project=self.project.key)
                fix_version_id = fix_version.id
            else:
                fix_version_id = version.id
        else:
            fix_version = self.get_versions()[-1]
            fix_version = self._jira.get_project_version_by_name(project=self.project.key, version_name=fix_version)
            fix_version_id = fix_version.id
        fix_versions = [{"id": fix_version_id}]
        return fix_versions

    def get_summary(self, parent_issue, task_name, task_type):
        if task_name is None and task_type in self.SUBTASK_RELEASE_TYPES:
            summary = " ".join([Summaries.all.get(task_type), parent_issue.fields.fixVersions[0].name])
        elif task_name is None:
            summary = " ".join([Summaries.all.get(task_type), parent_issue.fields.summary])
        else:
            summary = " ".join([Summaries.all.get(task_type), task_name])
        return summary

    def get_issue_type_id(self, task_type):
        issue_type_id = 0
        if task_type in [prop for prop in dir(TaskType.DevOps) if not prop.startswith("_")]:
            issue_type_id = IssueTypes().devops_sub_task_id
        elif task_type in [prop for prop in dir(TaskType.QA) if not prop.startswith("_")]:
            issue_type_id = IssueTypes().testing_sub_task_id
        elif task_type in [prop for prop in dir(TaskType.Pm) if not prop.startswith("_")]:
            issue_type_id = IssueTypes().sub_task_id
        elif task_type in [prop for prop in dir(TaskType.TechDoc) if not prop.startswith("_")]:
            issue_type_id = IssueTypes().sub_task_id
        return issue_type_id

    def update_original_estimate(self, key, hours=None):
        if hours is None:
            hours = 4
        else:
            hours = int(hours)
        issue = self.get_issue(task_key=key)
        try:
            issue.update(fields={"timetracking": {"originalEstimate": "%ih" % hours}})
        except Exception as e:
            logging.error(f"Не удалось обновить эстимейты {key}, установить значение {hours} в часах")
            logging.error(e)
        return self

    def create_subtask(
            self, parent_task_key, task_type=TaskType.QA.verification, assignee=None, task_name=None
    ) -> Issue | None:
        if assignee is None:
            assignee = self.get_assignee(task_type)
        sub_task = self.generate_subtask(
            parent_task_key=parent_task_key, task_type=task_type, assignee=assignee, task_name=task_name
        )
        assert self.validation_subtask(sub_task), "Валидация сгенерированной подзадачи не прошла"
        return self._jira.create_issue(fields=sub_task)

    @staticmethod
    def validation_subtask(data) -> bool:
        try:
            _ = json.dumps(data)
            return True
        except ValueError as e:
            print("Ошибка валидации", e.args[0])
            return False

    def is_parent_task(self, key):
        assert self.is_valid_jira_key(key), f"Неверно указан ключ проекта: {key}, пример: 'MYPROJECT1-123'"
        issue = self.get_issue(key)
        try:
            return not str(issue.fields.issuetype.name).lower().__contains__("sub-task")
        except Exception as e:
            print(e.args[0])
            logging.error(e.args[0])
        return False

    def get_issue_parent_key(self, key):
        issue = self.get_issue(key)
        return issue.fields.parent.key

    def get_versions(self, version_pattern=JIRA_RELEASE_PATTERN):
        all_project_version = self._jira.project_versions(self.project.key)
        versions = []
        for release_version in all_project_version:
            if re.match(version_pattern, release_version.name):
                versions.append(release_version.name)
        return versions

    def set_version_released(self, version):
        version = self._jira.get_project_version_by_name(self.project.key, version)
        if not version.released:
            version.update(released=True)
        assert version.released is True, f"Версия {version} не зарелизилась"
        return self

    def get_subtasks_all_statuses(self, parent_key) -> list:
        sts = self.get_child_tasks(parent_key=parent_key)
        return list(set([st.fields.status.name for st in sts]))

    def is_subtasks_all_statuses_closed(self, parent_key):
        statuses = set(self.get_subtasks_all_statuses(parent_key))
        return statuses == {"Closed"}

    def get_child_tasks(self, parent_key):
        jql_str = f'"Parent Link"={parent_key}'
        child_tasks = self._jira.search_issues(jql_str=jql_str)
        return child_tasks

    def get_subtasks_wo_qa(self, parent_key):
        jql_str = (
            f'"Parent Link"={parent_key} '
            f"and issuetype not in ({IssueTypes(project=self.project).testing_sub_task_id})"
        )
        child_tasks = self._jira.search_issues(jql_str=jql_str)
        return child_tasks

    def get_subtasks_o_qa(self, parent_key):
        jql_str = (
            f'"Parent Link"={parent_key} ' f"and issuetype in ({IssueTypes(project=self.project).testing_sub_task_id})"
        )
        child_tasks = self._jira.search_issues(jql_str=jql_str)
        return child_tasks

    def move_task_to_in_progress_safe(self, parent_key):
        subtask_statuses_positive = ["Ready for Test", "Testing", "In Progress", "Review"]
        expected_parent_status = ["In Progress", "Ready for Test", "Testing"]
        parent_issue = self.get_issue(task_key=parent_key)
        parent_status = parent_issue.fields.status.name
        child_tasks = self.get_subtasks_wo_qa(parent_key=parent_key)

        for subtask in child_tasks:
            if subtask.fields.status.name not in subtask_statuses_positive:
                continue
            if parent_status not in expected_parent_status:
                logging.warning(f"Родительская задача {parent_key} не совпадает со статусом дочерних {child_tasks}.")
                self.transition_issue(parent_issue=parent_issue, final_state="In progress")
        return True

    def is_issue_status(self, parent_key, status):
        return status == self.get_issue_status(task_key=parent_key)

    # todo: fix me
    def transition_issue(self, parent_issue, final_state=None):  # noqa: C901
        final_state, parent_issue = self.prepare_transitions(final_state, parent_issue)
        tries = 0

        while tries < 15 and not self.is_issue_status(parent_key=parent_issue, status=final_state):
            try:
                status_name = self.get_issue_status(task_key=parent_issue)
                if status_name == JiraIssueStatus.BACKLOG:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.TO_PBR.jira_id)
                elif status_name == JiraIssueStatus.PBR:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.READY_TO_WORK.jira_id)
                elif status_name == JiraIssueStatus.OPEN:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.START_WORK.jira_id)
                elif status_name == JiraIssueStatus.IN_PROGRESS:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.TO_DEVELOPMENT.jira_id)
                elif status_name == JiraIssueStatus.READY_FOR_DEVELOPMENT:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.START_DEVELOPMENT.jira_id)
                elif status_name == JiraIssueStatus.DEVELOPMENT:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.TO_REVIEW.jira_id)
                elif status_name == JiraIssueStatus.REVIEW:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.TO_TEST.jira_id)
                elif status_name == JiraIssueStatus.READY_FOR_TEST:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.START_TESTING.jira_id)
                elif status_name == JiraIssueStatus.TESTING:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.FINISH_TESTING.jira_id)
                elif status_name == JiraIssueStatus.READY_TO_CHECK:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.APPROVE.jira_id)
                elif status_name == JiraIssueStatus.READY_TO_INSTALL:
                    self._jira.transition_issue(parent_issue, JiraIssueTransitionStatuses.CLOSE.jira_id)
                elif status_name == JiraIssueStatus.CLOSED:
                    break
                logging.info(f"Поменяли статус у родительской задачи {self.get_issue(parent_issue.key)}")
            except jira.exceptions.JIRAError as e:
                tries = self.check_transition_error(e, parent_issue, status_name, tries)
            finally:
                time.sleep(0.5)
                tries += 1
                print("Попыток: ", tries)
        return self

    def prepare_transitions(self, final_state, parent_issue):
        if final_state is None:
            final_state = "In progress"
        if isinstance(parent_issue, jira.resources.Issue):
            parent_issue = self.get_issue(parent_issue.key)
        elif isinstance(parent_issue, str):
            parent_issue = self.get_issue(parent_issue)
        return final_state, parent_issue

    def check_transition_error(self, e, parent_issue, status_name, tries):
        err_msg_checklist = "All checklist items must be checked."
        err_msg_open_subtask = "You have open subtasks"
        err_msg_wf_operation = "It seems that you have tried to perform a workflow operation"
        print(f"Для задачи {parent_issue} не удалось поменять статус.")
        if status_name == JiraIssueStatus.READY_TO_INSTALL and err_msg_checklist in e.args:
            self.delete_smart_check_list(parent_issue)
        elif err_msg_open_subtask in e.args[0]:
            tries = 20
        elif err_msg_wf_operation in e.args[0]:
            tries = 20
        logging.error(e.args[0])
        print(e)
        return tries

    def create_release_task(self, fix_version_name, timeout=60):
        if not self.get_issue_release(fix_version_name=fix_version_name):
            release_issue = self.generate_release_issue(fix_version_name=fix_version_name)
            parent_issue = self._jira.create_issue(release_issue)
        else:
            parent_issue = self.get_issue_release(fix_version_name=fix_version_name)
        timeout += time.time()
        while time.time() < timeout:
            try:
                if isinstance(parent_issue, list):
                    parent_key = parent_issue[0].key
                elif isinstance(parent_issue, Issue):
                    parent_key = parent_issue.key
                break
            except Exception as e:
                logging.error(e)
                logging.error(f"Задача не создана {parent_issue}")
                print(f"Задача не создана {parent_issue}")
                time.sleep(1)
        for sub_task_type in self.SUBTASK_RELEASE_TYPES:
            if self.is_sub_task_exists(parent_task=parent_key, sub_task_type=sub_task_type):
                continue
            logging.info(f"Создаем под-задачу {sub_task_type} для {parent_key}")
            # try:
            subtask = self.create_subtask(parent_task_key=parent_key, task_type=sub_task_type)
            logging.info(f"Подзадача создана {subtask.key}:{subtask.fields.summary}")
            if subtask:
                default_estimate_hours = 8
                self.update_original_estimate(key=subtask.key, hours=default_estimate_hours)
                logging.info(f"Эстимейты проставлены {default_estimate_hours}: {subtask.key}:{subtask.fields.summary}")
            # except Exception as e:
            #
            #     logging.error(f"Ошибка при создании подзадачи {sub_task_type} для {parent_key}")

        logging.info("Создание задачи на релиз завершено.")
        return self

    def generate_release_issue(self, fix_version_name):
        if not re.match(JIRA_RELEASE_PATTERN, fix_version_name):
            raise NameError(f"fix_version не подходит по патерну {JIRA_RELEASE_PATTERN}")
        version = self._jira.get_project_version_by_name(project=self.project.key, version_name=fix_version_name)
        if not self.is_description_exist(fix_version_name):
            self.set_description(fix_version_name=fix_version_name)
        fix_versions = [{"id": version.id}]
        description = self.generate_release_description(fix_version=version.id)
        summary = f"Релиз {fix_version_name}"

        labels = ["release"]
        assignee = Users.qa_manager_login.name

        return {
            "project": self.project.key,
            "summary": summary,
            "description": description,
            "labels": labels,
            "assignee": {"name": assignee},
            "issuetype": {"id": IssueTypes().story_enabler_id},
            "fixVersions": fix_versions,
        }

    def generate_release_description(self, fix_version):
        version = self._jira.version(fix_version)
        release_link = f"[Релизы|{HTTPS_CONFLUENCE_URL}/pages/viewpage.action?pageId={self.project.release_page_id}]"
        description = f"""Цели релиза:
        {version.description}
        Запланированная дата установки в продуктивную среду - {version.releaseDate if version.releaseDate else 'TBD'}
        Описание релиза доступно по ссылке - {release_link}
        """
        return description

    def get_qa_verification_task(self, fix_version):
        qa_verification_task = None
        release_issue = self.get_issue_release(fix_version_name=fix_version)
        if release_issue is None:
            raise NameError(f"Релизных задач в проекте {self.project.key} для версии {fix_version} не найдено!")
        child_tasks = self.get_child_tasks(release_issue)
        for child in child_tasks:
            if f"Верификация релиза {fix_version}" in child.fields.summary:
                qa_verification_task = child
                break
        return qa_verification_task

    def get_issue_release(self, fix_version_name):
        release_issue = None
        jql_str = (
            f'project = {self.project.key} AND summary ~  "Релиз {fix_version_name}" AND type in ("Story Enabler")'
        )
        release_issues = self._jira.search_issues(jql_str=jql_str)
        if len(release_issues) == 0:
            print(f'Задача на релиз не создана.')
            logging.error(f'Задача на релиз не создана.')
        elif len(release_issues) > 1:
            f"Ожидалось что есть только 1 задача на релиз, получили больше одной: {release_issues}"
        # assert len(release_issues) == 1
        elif len(release_issues) == 1:
            release_issue = release_issues[0]
        return release_issue

    def get_issues_release_qa_subtasks(self, fix_version_name):
        jql_str = (
            f'issueFunction in subtasksOf("project = {self.project.key} AND fixVersion = {fix_version_name}")'
            f' AND issuetype = "Testing Sub-task" AND status not in (Closed)'
        )

        return self._jira.search_issues(jql_str=jql_str)

    def is_epic(self, key) -> bool:
        try:
            issue = self.get_issue(task_key=key)
            return int(issue.fields.issuetype.id) == IssueTypes.epic_id
        except Exception as e:
            logging.error(e)
        return False

    def is_bug(self, key) -> bool:
        try:
            issue = self.get_issue(task_key=key)
            return int(issue.fields.issuetype.id) == IssueTypes.bug_id
        except Exception as e:
            logging.error(e)
        return False

    def get_issues_release_notes(self, fix_version_name):
        jql_str = (
            f'project = {self.project} AND fixVersion = {fix_version_name} and type in (Story,"Story Enabler", "Bug")'
            f"and (labels not in (release) or labels is EMPTY)"
        )
        return self.get_issues_jql(jql_str=jql_str)

    def is_description_exist(self, fix_version_name):
        version = self._jira.get_project_version_by_name(project=self.project.key, version_name=fix_version_name)
        try:
            return len(version.description) > 0
        except Exception:
            logging.error(f"Нет описания для {self.project.key}:{fix_version_name}")
            return False

    def set_description(self, fix_version_name, description=None):
        if description is None:
            issues = self.get_issues_release_notes(fix_version_name=fix_version_name)
            if len(issues) == 0:
                raise NameError(
                    f"В версии {fix_version_name} нет jira задачи для цели релиза, "
                    f"установите цель релиза вида: MYPROJECT1-123 Добавить новую функцию"
                )
            description = ",".join([issue.key for issue in issues])
        version = self._jira.get_project_version_by_name(self.project.key, fix_version_name)
        version.update(description=description)
        return self

    def get_assignee(self, task_type: TaskType):
        assignee = [
            user for user in getattr(Users, self.project.key.lower()) if task_type in user.responsibilities.task_types
        ]
        if len(assignee) == 0:
            raise NameError(
                f"Исполнитель не проекте {self.project.name}, для задачи {task_type}, не найден, наймите еще людей."
            )
        else:
            assignee = assignee[0]
        return assignee

    @staticmethod
    def is_valid_jira_key(key) -> bool:
        jira_key_pattern = r"^\w+-\d+$"
        return True if re.match(jira_key_pattern, key) else False

    def is_story_or_story_enabler(self, key) -> bool:
        try:
            issue = self.get_issue(task_key=key)
            return int(issue.fields.issuetype.id) in (IssueTypes.story_id, IssueTypes.story_enabler_id)
        except Exception as e:
            logging.error(e)
        return False

    def move_issues_to_closed(self, fix_version_name):
        issues = self.get_issues_all_in_release(fix_version_name=fix_version_name, without_closed_issue=True)
        for issue in issues:
            self.transition_issue(issue, JiraIssueTransitionStatuses.CLOSE)
        return self

    def is_fix_version_exists(self, fix_version):
        versions = self.get_versions()
        for version in versions:
            if fix_version == version:
                return True
        return False

    def get_issues_all_in_release(self, fix_version_name, without_closed_issue):
        logging.info("Получить все задачи в релизе")
        if not self.is_fix_version_exists(fix_version=fix_version_name):
            raise NameError(f"FixVersion {fix_version_name} не создан в Jira!!!")
        jql = (
            f"project = {self.project.jira_id} AND fixVersion = {fix_version_name} "
            f"and (labels not in (release, noqa, noQA) or labels is EMPTY )"
        )
        if without_closed_issue:
            jql += " and status != Closed"
        release_tasks = self.get_issues_jql(jql_str=jql)
        return release_tasks

    def move_parent_task_to_actual_status(self, parent_key):
        if not self.is_parent_task(parent_key):
            logging.warning("Задача не является родительской")
            return False
        if self.is_subtasks_all_statuses_closed(parent_key):
            self.transition_issue(parent_issue=parent_key, final_state=JiraIssueStatus.CLOSED)
        elif JiraIssueStatus.TESTING in self.get_subtasks_all_statuses(parent_key):
            self.transition_issue(parent_issue=parent_key, final_state=JiraIssueStatus.TESTING)
        elif JiraIssueStatus.READY_FOR_TEST in self.get_subtasks_all_statuses(parent_key):
            self.transition_issue(parent_issue=parent_key, final_state=JiraIssueStatus.READY_FOR_TEST)
        elif JiraIssueStatus.IN_PROGRESS in self.get_subtasks_all_statuses(parent_key):
            self.transition_issue(parent_issue=parent_key, final_state=JiraIssueStatus.IN_PROGRESS)
        elif JiraIssueStatus.OPEN in self.get_subtasks_all_statuses(parent_key):
            no_qa_tasks = self.get_subtasks_wo_qa(parent_key=parent_key)
            for task in no_qa_tasks:
                if task.fields.status.name == JiraIssueStatus.OPEN:
                    self.transition_issue(parent_issue=parent_key, final_state=JiraIssueStatus.IN_PROGRESS)
                    break
            qa_tasks = self.get_subtasks_o_qa(parent_key=parent_key)
            for task in qa_tasks:
                if task.fields.status.name == JiraIssueStatus.OPEN:
                    if TaskType.QA.verification in task.fields.labels:
                        self.transition_issue(parent_issue=parent_key, final_state=JiraIssueStatus.TESTING)
                        break
                    else:
                        logging.info(
                            "Quality gates не выполнены, надо закрыть задачи по тестированию до выпуска релиза"
                        )
                        continue
        else:
            logging.info(f"Задача: {parent_key} не соответствует статусной модели.")
        return True

    def delete_smart_check_list(self, issue="MYPROJECT1-1960") -> bool:
        result = False
        if isinstance(issue, str):
            pass
        elif isinstance(issue, Issue):
            issue = issue.key
        url = f"{HTTPS_JIRA_URL}/rest/api/2/issue/{issue}/properties/com.railsware.SmartChecklist.checklist"
        payload = json.dumps("")
        r.put(url=url, auth=self.basic_auth, data=payload, verify=False, headers=self.headers)
        issue = self.get_issue(issue)
        if issue.fields.customfield_13701 is None:
            print("Чек лист очищен {issue}")
            result = True
        else:
            print(f"Чек лист не очищен {issue}: {issue.fields.customfield_13701}")
        return result

    def move_subtask_qa_to_debt_story(self, fix_version_name, qa_debt_key=None, label=Labels.qa_debt,
                                      ignore_release_task=True):

        qa_debt_key = self.get_qa_debt_key() if qa_debt_key is None else qa_debt_key
        qa_sub_tasks = self.get_issues_release_qa_subtasks(fix_version_name=fix_version_name)
        ignore_tasks = ['Установить тег для автотестов', 'Верификация релиза']

        for qa_sub_task in qa_sub_tasks:
            skip = False
            if ignore_release_task:
                for ignore_task in ignore_tasks:
                    if ignore_task in qa_sub_task.fields.summary:
                        skip = True
                        break
            if skip:
                continue
            parent_key = self.get_issue_parent_key(qa_sub_task)
            issue_key = qa_sub_task.key
            labels = qa_sub_task.fields.labels
            if label not in labels:
                labels.append(label)
            qa_sub_task.update(fields={"labels": labels, "versions": [{"name": fix_version_name}]})
            self._jira.create_issue_link(
                type="child of",
                inwardIssue=issue_key,
                outwardIssue=parent_key,
                comment={
                    "body": f"Задача {qa_sub_task.key} вынесена из релиза так как не успели ее"
                            f" сделать в рамках релиза {fix_version_name}."
                },
            )
            self.move_from_story_to_another_story_v3(subtask_id=qa_sub_task.id, parent_key=qa_debt_key)
        return self

    def get_token_jsession(self, subtask_id):
        s = requests.session()
        response = s.get(
            HTTPS_JIRA_URL + "/secure/MoveSubTaskChooseOperation!default.jspa",
            params={"id": subtask_id},
            auth=self.basic_auth,
            verify=False,
        )
        jsessionid = response.cookies.get("JSESSIONID")
        token = response.cookies.get("atlassian.xsrf.token")
        return jsessionid, token

    def move_from_story_to_another_story_v3(self, subtask_id, parent_key="MYPROJECT1-1877"):
        s = requests.session()
        jsessionid, token = self.get_token_jsession(subtask_id)
        params = {"atl_token": token, "id": subtask_id}
        data = {"parentIssue": parent_key, "id": subtask_id, "Change+Parent": "Change+Parent", "atl_token": token}
        cookies = {"some_id": self.headers.get("some_id")}
        url = self.server + "/foo/bar"
        response = s.post(url, params=params, data=data, cookies=cookies, verify=False)
        return response

    def get_qa_debt_key(self):
        if self.project == Projects.MYPROJECT1:
            qa_debt_key = "MYPROJECT1-122"
        elif self.project == Projects.MYPROJECT2:
            qa_debt_key = "MYPROJECT2-123"
        else:
            raise NameError(f"Задайте задачу для долгов по тестирования для проекта: {self.project}")
        return qa_debt_key
