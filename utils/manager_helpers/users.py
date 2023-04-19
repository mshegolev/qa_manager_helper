from utils.manager_helpers.constants import TaskType


class Roles:
    manual = "manual"
    auto = "auto"
    any = "any"
    techdoc = "techdoc"
    pm = "pm"
    devops = "devops"


class Responsibilities:
    def __init__(self, role=None):
        if role is None or role == Roles.any:
            self.task_types = [TaskType.Any.any]
        elif role == Roles.manual:
            self.task_types = [
                TaskType.QA.manual,
                TaskType.QA.verification,
                TaskType.QA.demo,
                TaskType.QA.release_verification,
            ]
        elif role == Roles.auto:
            self.task_types = [TaskType.QA.auto, TaskType.QA.autotest_tag, TaskType.QA.verify_auto]
        elif role == Roles.pm:
            self.task_types = [TaskType.Pm.check_tasks]
        elif role == Roles.devops:
            self.task_types = [task for task in dir(TaskType.DevOps) if not task.startswith("_")]
        elif role == Roles.techdoc:
            self.task_types = [TaskType.TechDoc.techdoc, TaskType.TechDoc.release_notes]


class Engineer:
    def __init__(self, name=None, qualification=None, responsibilities: list[TaskType] = None):
        if name is None:
            self.name = "default_qa_system_user_login"
        else:
            self.name = name
        if qualification is None:
            self.qualification = Roles.any
        else:
            self.qualification = qualification

        if responsibilities is None:
            self.responsibilities = Responsibilities(self.qualification)
        else:
            self.responsibilities = responsibilities

    def __repr__(self):
        return self.name


class Users(Engineer):
    default_qa_system_user_login = Engineer()
    qa_manager_login = Engineer(name="qa_manager_login", qualification=Roles.any)
    qa_manual2_login = Engineer(name="qa_manual2_login", qualification=Roles.manual)
    qa_manual_login = Engineer(name="qa_manual_login", qualification=Roles.manual)
    qa_manual_3_login = Engineer(name="qa_manual_3_login", qualification=Roles.manual)
    techwriter_login = Engineer(name="techwriter_login", qualification=Roles.techdoc)
    qa_auto_login = Engineer(name="qa_auto_login", qualification=Roles.auto)
    devops1_login = Engineer(name="devops1_login", qualification=Roles.devops)
    devops2_login = Engineer(name="devops2_login", qualification=Roles.devops)
    pm_login = Engineer(name="pm_login", qualification=Roles.pm)
    pm1_login = Engineer(name="pm1_login", qualification=Roles.pm)
    MYPROJECT1 = [qa_manager_login, qa_manual2_login, qa_manual_login, techwriter_login, qa_auto_login, pm_login, devops1_login, default_qa_system_user_login]
    MYPROJECT2 = [qa_manual_3_login, qa_manager_login, devops2_login, pm1_login]
    MYPROJECT3 = [qa_manager_login, devops2_login, pm1_login]
