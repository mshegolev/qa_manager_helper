import argparse

import urllib3

from utils.manager_helpers.constants import Projects, TaskType, Project
from utils.manager_helpers.jira_helper import JiraHelper
from utils.manager_helpers.users import Users, Engineer

urllib3.disable_warnings()


def create_tasks(parent_key: str, tasks: list, assignees):
    project = get_project_by_parent_key(parent_key)
    j = JiraHelper(project=project)
    if isinstance(tasks, str):
        tasks = [tasks]
    elif not isinstance(tasks, list):
        raise NameError("В метод можно передовать только задачу или список задач")
    if isinstance(assignees, str):
        assignees = [assignees]
    elif isinstance(assignees, Engineer):
        assignees = [assignees.name]
    elif not isinstance(assignees, list):
        raise NameError("В метод можно передовать только иполнителя или список исполнителей")

    for current_assignee in assignees:
        for task_type in tasks:
            # todo: if parent_key is sabtask, crate subtask for parrent_key and set the name of checked subtask
            task_name = None
            if not j.is_parent_task(key=parent_key):
                task_name = j.get_issue(parent_key).fields.summary
                parent_key = j.get_issue_parent_key(key=parent_key)
            if not j.is_parent_task(key=parent_key):
                print("ERROR: this is not a parrent task!!!!")
                continue
            if j.is_sub_task_exists(parent_task=parent_key, sub_task_type=task_type):
                print(f"WARNING: already created {parent_key} subtask type: {task_type}")
                continue
            issue = j.create_subtask(
                parent_task_key=parent_key, task_type=task_type, assignee=current_assignee, task_name=task_name
            )
            print("INFO: New task created ", parent_key, issue.id, issue.key, current_assignee, task_type)


def do(parent: str = None, task_types: list = None, project: Projects = None):
    validation_key_and_project(parent, project)
    if not project:
        project = Projects.MYPROJECT1
    j = JiraHelper(project=project)
    parent_issues = [parent] if parent else j.get_all_story_keys()
    task_types = task_types if task_types else TaskType.QA.all

    for parent_issue in parent_issues:
        for issue_type in task_types:
            if not j.is_sub_task_exists(parent_task=parent_issue, sub_task_type=issue_type):
                j.create_subtask(parent_task_key=parent_issue, task_type=issue_type)


def validation_key_and_project(parent, project):
    if parent and project:
        assert project in parent, "Задача от другого проекта"
    if project:
        assert project in [Projects.MYPROJECT1, Projects.MYPROJECT2]


def get_auto_qa(project) -> str:
    engineer = Users.default_qa_system_user_login
    if Projects.MYPROJECT1.key in project:
        engineer = Users.qa_auto_login
    elif Projects.MYPROJECT2.key in project:
        engineer = Users.default_qa_system_user_login
    elif Projects.MYPROJECT3.key in project:
        engineer = Users.default_qa_system_user_login
    return engineer


def get_manual_qa(project) -> str:
    engineer = Users.default_qa_system_user_login
    if Projects.MYPROJECT1.key in project:
        engineer = Users.qa_manual2_login
    elif Projects.MYPROJECT2.key in project:
        engineer = Users.qa_manual_3_login
    elif Projects.MYPROJECT3.key in project:
        engineer = Users.ovdani15
    return engineer


def create_all_qa_with_assignee(parent_key, manual_qa=None, auto_qa=None, tasks=None):
    assignee = None
    manual_qa_tasks = [
        TaskType.QA.manual,
        TaskType.QA.verification,
        TaskType.DevOps.deploy_stage,
        TaskType.TechDoc.techdoc,
    ]
    aqa_tasks = [TaskType.QA.auto]
    if tasks is None:
        tasks = manual_qa_tasks + aqa_tasks
    elif isinstance(tasks, str):
        tasks = [tasks]

    is_valid_key(parent_key)
    project = get_project_by_parent_key(parent_key)

    for task in tasks:
        if task in manual_qa_tasks:
            assignee = get_manual_qa(project)
        elif task in aqa_tasks:
            assignee = get_auto_qa(project)
        create_tasks(parent_key=parent_key, tasks=task, assignees=assignee)


def is_valid_key(issue_key):
    assert issue_key != "", "Задайте номер родительской задачи"
    is_valid = False
    for project in [prop for prop in dir(Projects) if not str(prop).startswith("_")]:
        if project.lower() in issue_key.lower():
            is_valid = True
    assert is_valid, f"Задача {issue_key} от другого проекта"


def get_project_by_parent_key(issue_key) -> str:
    is_valid_key(issue_key)
    project = ""
    if Projects.MYPROJECT1 in issue_key:
        project = Projects.MYPROJECT1
    elif Projects.MYPROJECT2 in issue_key:
        project = Projects.MYPROJECT2
    elif Projects.MYPROJECT3 in issue_key:
        project = Projects.MYPROJECT3
    return project


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", type=str, dest="key", help="Parrent issue key, example: MYPROJECT1-439", default=None)
    parser.add_argument(
        "-jdi",
        "--just_do_it",
        dest="just_do_it",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If you need to do all, just enable do, example: --just_do_it",
    )
    args = parser.parse_args()
    for _ in args._get_kwargs():
        globals()[f"{_[0]}"] = _[1]
    return globals()


def get_jira_issues_for_test(project: Projects.MYPROJECT1.key, fixVersion):
    if isinstance(project, Project):
        project_key = project.key
    elif isinstance(project, str):
        assert project in Projects.any, f"{project} Не найден в существующих проектах {Projects.any}"
        project_key = project
    elif not isinstance(project, str):
        raise NameError("Укажите корректный проект MYPROJECT1, MYPROJECT2, MYPROJECT3")
    j = JiraHelper(project=project)
    if project == Projects.MYPROJECT3:
        jql_str = (
            f"project={project_key} and fixVersion={fixVersion} "
            f'and type in ("Story", "Story Enabler") and (labels !=qa_skip or labels is EMPTY )'
        )
    elif project == Projects.MYPROJECT1:
        jql_str = (
            f"project={project_key} and fixVersion={fixVersion} "
            f'and type in ("Story", "Story Enabler") and (labels !=qa_skip or labels is EMPTY )'
        )

    else:
        raise NameError("Нужно сформировать запрос для получения историй на тестирование")
    issues = j.get_issues_jql(jql_str=jql_str)
    return [issue.key for issue in issues]


if __name__ == "__main__":
    arg_parser()

    key = "MYPROJECT1-2056"

    keys = []
    # keys = get_jira_issues_for_test(project=Projects.MYPROJECT1, fixVersion="v0.15.0")

    if keys:
        for _ in keys:
            print(f"create task with {_}")
            create_all_qa_with_assignee(parent_key=_, tasks=TaskType.QA.verify_auto)
    if key:
        print(f"create task with {key}")
        create_all_qa_with_assignee(key)
    # if just_do_it:
    #     print("You choose JUST DO IT, LETS ROCK!!!")
    #     do()
    #     print("ENJOY!!!")

    # task_types = [TaskType.TechDoc.techdoc]
    # assignees = Users.techwriter_login
    # create_tasks(parent_key=key, tasks=task_types, assignees=assignees)
