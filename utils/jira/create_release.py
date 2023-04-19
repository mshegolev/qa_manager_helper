from utils.manager_helpers.constants import Projects
from utils.manager_helpers.release_creator import ReleaseCreator

if __name__ == "__main__":
    project = Projects.MYPROJECT2
    fix_version = "v1.0.0"

    send_planning_mail = False
    move_qa_debt = False
    create = True
    released = False
    task_moving = False

    release = ReleaseCreator(project=project, fix_version=fix_version)
    if task_moving:
        release.set_actual_status_for_story(fix_version=fix_version)

    if create:
        release.prepare_all_tasks_in_release(fix_version=fix_version, ignore_closed=True)
        release.set_actual_status_for_story(fix_version=fix_version)
        release.create_release(fix_version_name=fix_version)
    if send_planning_mail:
        release.send_email_plan_to_install(fix_version='v1.0.1', install_date='19.04.2033',
                                           install_time='с 09:00 до 10:00',
                                           devops='Фамилия Имя', qa_verification_task='MYPROJECT1-200000',
                                           dry_run=True)
    if move_qa_debt:
        release.JiraHelper.move_subtask_qa_to_debt_story(fix_version_name=fix_version, ignore_release_task=True)
    if released:
        release.JiraHelper.move_subtask_qa_to_debt_story(fix_version_name=fix_version)
        release.close_release(fix_version=fix_version)
