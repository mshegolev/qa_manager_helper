import logging

from utils.confluence.confluence_helper import ConfluenceHelper
from utils.constants import HTTPS_CONFLUENCE_URL
from utils.manager_helpers.constants import Project, Projects, TaskType
from utils.manager_helpers.issue_types import IssueTypes
from utils.manager_helpers.jira_helper import JiraHelper, JiraIssueStatus
from utils.manager_helpers.mail_helper import MailHelper


class ReleaseCreator:
    def __init__(self, project: Project = Projects.MYPROJECT1, fix_version=None):
        if isinstance(project, str):
            self.project = getattr(Projects, project.upper())
        elif isinstance(project, Project):
            self.project = project
        self.JiraHelper = JiraHelper(project=self.project)
        self.MailHelper = MailHelper()
        self.ConfluenceHelper = ConfluenceHelper(project=self.project)
        if fix_version is None:
            self.fix_version = self.JiraHelper.get_versions()
            if len(self.fix_version) == 0:
                raise NameError("Нужно создать релиз в Jira.")
            elif len(self.fix_version) == 1:
                self.fix_version = self.fix_version[0]
            elif len(self.fix_version) >= 2:
                self.fix_version = self.fix_version[-2]

    def prepare_all_tasks_in_release(self, fix_version, ignore_closed=True):
        release_tasks = self.JiraHelper.get_issues_all_in_release(
            fix_version_name=fix_version, without_closed_issue=ignore_closed
        )
        for task in release_tasks:
            if int(task.fields.issuetype.id) == IssueTypes.development_sub_task_id:
                # 1. если задача разработчика, то проверить кто парент
                # 1.1. для парента story, story enabler проверить что есть подзадачи на тестирование
                # установить версию для тестирования 23Q1-для MYPROJECT1, для остальных оставить пустое поле
                # 1.2. если парент epic то пропустить
                #
                parent = self.JiraHelper._jira.issue(task.fields.parent.key)
                if int(parent.fields.issuetype.id) == IssueTypes.epic_id:
                    self.create_qa_sub_task_if_not_exist(parent)
                elif int(parent.fields.issuetype.id) == IssueTypes.story_id:
                    if self.same_versions(keys=[parent.key, task.key]):
                        self.create_qa_sub_task_if_not_exist(parent)
                    else:
                        print(
                            f"Версия Story{parent.fields.fixVersions} не совпадает с "
                            f"версией подзадачи {task.fields.fixVersions}"
                        )
                elif int(parent.fields.issuetype.id) == IssueTypes.story_enabler_id:
                    self.create_qa_sub_task_if_not_exist(parent)
            elif int(task.fields.issuetype.id) in [
                IssueTypes.analytics_sub_task_id,
                IssueTypes.sub_task_id,
                IssueTypes.devops_sub_task_id,
                IssueTypes.testing_sub_task_id,
            ]:
                continue

            elif int(task.fields.issuetype.id) in [
                IssueTypes.epic_id,
                IssueTypes.story_id,
                IssueTypes.story_enabler_id,
            ]:
                if task.fields.status.name == "Closed":
                    continue
                assert self.JiraHelper.move_task_to_in_progress_safe(parent_key=task.key)
                self.create_qa_sub_task_if_not_exist(task.key)
            elif int(task.fields.issuetype.id) in [IssueTypes.bug_id]:
                continue
        return self

    def get_all_tasks_in_release(self, fix_version, ignore_closed):
        release_tasks = self.JiraHelper.get_issues_all_in_release(fix_version, ignore_closed)
        return release_tasks

    def set_actual_status_for_story(self, fix_version):
        tasks = [
            task.key
            for task in self.JiraHelper.get_issues_all_in_release(
                fix_version_name=fix_version, without_closed_issue=True
            )
        ]
        for task in tasks:
            if self.JiraHelper.is_story_or_story_enabler(key=task):
                self.JiraHelper.move_parent_task_to_actual_status(parent_key=task)
        return self

    def create_qa_sub_task_if_not_exist(self, parent):
        if self.project.key in (Projects.MYPROJECT2.key, Projects.MYPROJECT3.key):
            task_types = [TaskType.QA.verification, TaskType.QA.manual]
            msg = f"Нанять автоматизатора на проект {self.project.name}!"
            print("WARNING", msg)
            logging.warning(msg)
        else:
            task_types = [TaskType.QA.verification, TaskType.QA.manual, TaskType.QA.auto]
        for task_type in task_types:
            if self.JiraHelper.is_epic(key=parent) or self.JiraHelper.is_bug(key=parent):
                logging.info(f"К эпикам и багам {parent} не создаем подзадачи на тестирование, только к историям.")
                continue
            if not self.JiraHelper.is_sub_task_exists(parent_task=parent, sub_task_type=task_type):
                sub_task = self.JiraHelper.create_subtask(parent_task_key=parent, task_type=task_type)
                if sub_task:
                    self.JiraHelper.update_original_estimate(sub_task.key)
        return self

    def same_versions(self, keys: list):
        versions = []
        if len(keys) > 1:
            for key in keys:
                task = self.JiraHelper.get_issue(key)
                try:
                    versions.append(task.fields.fixVersions[0].id)
                except IndexError:
                    return False
        return len(set(versions)) == 1

    def create_release(self, fix_version_name):
        self.JiraHelper.create_release_task(fix_version_name=fix_version_name)
        self.ConfluenceHelper.create_release_page(fix_version=fix_version_name)
        return self

    def close_release_task(self, fix_version_name):
        self.JiraHelper.move_subtask_qa_to_debt_story(fix_version_name=fix_version_name)
        self.JiraHelper.move_issues_to_closed(fix_version_name=fix_version_name)
        release_issue = self.JiraHelper.get_issue_release(fix_version_name=fix_version_name)
        self.JiraHelper.transition_issue(release_issue, JiraIssueStatus.CLOSED)
        return self

    def send_email_start_installing(self, fix_version):
        email_address = "group@r.ru"
        subject = "Установка релиза в продуктивную среду"
        message = f"""Всем привет!
    Мы начинаем работы по установке релиза {fix_version} в продуктивную среду.
            """
        assert self.MailHelper.send_email(subject=subject, message=message, email_address=email_address)

    def send_email_finish_installing(self, fix_version):
        email_address = "ep@r.ru"
        subject = "Установка релиза в продуктивную среду"
        message = f"""Всем привет!
    Работы по установке релиза{fix_version} в продуктивную среду завершены успешно.
                    """
        assert self.MailHelper.send_email(subject=subject, message=message, email_address=email_address)

    def send_email_plan_to_install(
            self, fix_version, install_date, install_time=None, devops=None, qa_verification_task=None,
            confluence_release_link=None, dry_run=True
    ):
        """
        @param fix_version - версия релиза для установки в прод
        @param install_date - дата установки
        @param install_time - вермя установки
        @param devops - исполнитель, кто будет устанавливать
        @param qa_verification_task - задача на верификацию релиза
        @param confluence_release_link - значение по умолчанию ${HTTPS_CONFLUENCE_URL}
        @param dry_run - Вывести на печать письмо, БЕЗ отправки по почте если True.

        Пример:
        fix_version='v0.16.1', install_date='13.04.2023', install_time='с 09:00 до 10:00',
        devops='Фамилия Имя', qa_verification_task='MYPROJECT1-2095',
        confluence_release_link=None', dry_run=True
        """
        if qa_verification_task is None:
            qa_verification_task = self.JiraHelper.get_qa_verification_task(fix_version)
        elif isinstance(qa_verification_task, str):
            qa_verification_task = self.JiraHelper.get_issue(qa_verification_task)
        if install_time is None:
            install_time = "с 09:00 до 10:00"
        if devops is None:
            if self.project == Projects.MYPROJECT1:
                devops = "Фамилия Имя"
            elif self.project in (Projects.MYPROJECT3, Projects.MYPROJECT3):
                devops = "Фамилия Имя"
            else:
                print(f"Назначьте devops инженера на проект {self.project}")
        release_page = HTTPS_CONFLUENCE_URL+"/pages/viewpage.action?pageId=123"
        goal_of_release = self.ConfluenceHelper.generate_goals_section(fix_version=fix_version)
        assert len(goal_of_release) != 0, "Цели релиза не заданы"
        qa_act = f"Акт приложен к задаче {qa_verification_task.permalink()}"
        install_period = f"{install_date}, СО {install_time} (+3 UTC) время по Москве."

        if confluence_release_link is None:
            confluence_release_link = self.ConfluenceHelper.get_release_page_link(fix_version=fix_version)

        email_address = "ep@r.ru"
        subject = "Установка релиза в продуктивную среду"
        message = f"""Всем привет!
    Мы планируем выпустить релиз “MYSUBPROJECT1_NAME” в продуктивную среду {install_period}
    Просьба разослать заинтересованным лицам.
    С описанием вошедших в релиз задач можно ознакомиться по ссылке:
    {confluence_release_link}

    Дополнительная информация:
    Будет установлена версия {fix_version}
    Февральская версия остается работать без изменений.

    RFC:
    Выполнение установки: {devops}.
    Плановые работы будут проводиться {install_date} {install_time} (+3 UTC)

    1 Краткое описание работ: Установка релиза PI {fix_version} {confluence_release_link}
    2 Оценка рисков: нет
    3 Недоступные процессы: нет
    4 Цель работ : установить релиз PI {fix_version}
    5 Причина изменений: {goal_of_release}
    6. Описание зависимостей: нет
    7. Меняется ли схема федерации: нет
    8. Описание проводимых работ: Установка PI в продуктивную среду
    Инструкция по внесению изменений - {release_page}
    9. Описание плана отката: (Инструкция по отмене внесенных изменений) - {release_page}
    10. Влияние на пользователя: нет
    11. Тестирование, когда, где и кем проведено (приложить акт): {qa_act}
    """
        self.MailHelper.is_email_exist(subject=subject, message=message, email_address=email_address)
        if not dry_run:
            assert self.MailHelper.send_email(subject=subject, message=message, email_address=email_address)
            pass
        print(f'{email_address=}')
        print(f'{subject=}')
        print(f'{message=}')

    def close_release(self, fix_version):
        self.set_actual_status_for_story(fix_version=fix_version)
        self.close_release_task(fix_version_name=fix_version)
        self.JiraHelper.set_version_released(fix_version)

        return self
