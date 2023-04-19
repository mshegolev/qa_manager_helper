from utils.manager_helpers.constants import Projects, TaskType


class IssueTypes:
    testing_sub_task_id = 1
    sub_task_id = 2
    development_sub_task_id = 3
    story_id = 4
    story_enabler_id = 5
    epic_id = 6
    devops_sub_task_id = 7
    analytics_sub_task_id = 8
    bug_id = 9

    def __init__(self, project=Projects.MYPROJECT1):
        if project == Projects.MYPROJECT1:
            self.testing_sub_task_id = 1
            self.sub_task_id = 2
            self.development_sub_task_id = 3
            self.story_id = 4
            self.epic_id = 6
            self.devops_sub_task_id = 7
            self.story_enabler_id = 5
            self.analytics_sub_task_id = 8
            self.bug_id = 9
        elif project == Projects.MYPROJECT2:
            self.story_id = 4
            self.epic_id = 6
            self.bug_id = 9
            self.story_enabler_id = 5
            self.testing_sub_task_id = 1
            self.sub_task_id = 99
            self.devops_sub_task_id = 7
        elif project == Projects.MYPROJECT3:
            self.testing_sub_task_id = 1
            self.bug_id = 9
            self.devops_sub_task_id = 7
            self.sub_task_id = 2
            self.development_sub_task_id = 3
            self.story_id = 4
            self.epic_id = 6
            self.story_enabler_id = 5
            self.analytics_sub_task_id = 8


SUBTASK_RELEASE_TYPES = [
    TaskType.Pm.check_tasks,
    TaskType.TechDoc.release_notes,
    TaskType.DevOps.deploy_stage,
    TaskType.QA.release_verification,
    TaskType.DevOps.resolve_session,
    TaskType.QA.autotest_tag,
    TaskType.DevOps.deploy_prodlike,
    TaskType.DevOps.mr_release_to_master,
    TaskType.DevOps.deploy_prod,
]
