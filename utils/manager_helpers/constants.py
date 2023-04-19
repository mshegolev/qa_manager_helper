QA_VERIFICATION_DESCRIPTION = """
todo:
Верифицировать историю по созданным тест кейсам

acceptance criteria:
1. Тест ран в testops прилинкован к задаче и к истории
"""  # noqa: W291
AUTOTESTS_DESCRIPTION = """
todo:
Написать / обновить автотесты

acceptance criteria:
1. тест ран в тестопс прилинкован к задаче
"""  # noqa: W291
LOAD_DESCRIPTION = """
todo:
Провести НТ

acceptance criteria:
1. Отчет о НТ прикреплен к задаче
2. тест ран в тестопс прилинкован к задаче
"""  # noqa: W291
MANUAL_DESCRIPTION = """
todo:
Обновить / создать ручные тест кейсы.

acceptance criteria:
1. тест кейсы созданые в testops и прилинкованы к задаче
"""  # noqa: W291
DEMO_DESCRIPTION = """
todo:
1. Подгтовить данные для демонстрации.
2. Провести демонстрацию.
3. Согласовать время проведения демонстрации с командами от которых зависит работа GraphQL и смежных систем.
4. Согласовать с командами расписание обновлений систем, отложить демо/обновление если пересекается по времени.
5. Согласовать расписание НТ на проверяемые системы или подсистемы. 

acceptance criteria:
1. Тестовые данные подготовлены (запросы/ответы) сохранены локально. Тестовые данные опубликованы в
в соответствующем проекте.
2. Время демо согласовано с командами которые отвечают за сопрягаемые системы и подсистемы.
"""  # noqa: W291
CREATE_TECH_DOCUMENTS = """
todo:
1. Создать/обновить документацию по задаче.

dod:
1. Ссылка на страницу прикреплена к задаче.
2. Есть комментарий тестировщика что документацию соответствует заявленным тербованиям.
"""
EDUCATION = """
todo:
1. Пройти обучение по программе в родительской задаче.

dod:
1. Обучение пройдено, сертификат получен.
"""


class QA:
    verification = "verification"
    auto = "auto"
    manual = "manual"
    load = "load"
    demo = "demo"
    release = "release"
    autotest_tag = "autotest_tag"
    release_verification = release + "_" + verification
    verify_auto = [verification, auto, manual]
    all = [verification, auto, manual, load, demo]


class Any:
    any = "any"
    education = "education"


class TechDoc:
    techdoc = "techdoc"
    release_notes = "release_notes"


class Pm:
    check_tasks = "check_tasks"


class Support:
    support = "support"


class DevOps:
    deploy_prod = "deploy_prod"
    deploy_stage = "deploy_stage"
    deploy_prodlike = "deploy_prodlike"
    resolve_session = "resolve_session"
    migration = "migration"
    devops = "devops"
    mr_release_to_master = "mr_release_to_master"


class TaskType:
    QA = QA
    TechDoc = TechDoc
    Any = Any
    DevOps = DevOps
    Pm = Pm


class IgnoreLabels:
    release = "release"
    noqa = "noqa"
    noQA = "noQA"


class Labels:
    qc = "QC"
    qa = "QA"
    aqa = "AQA"
    lqa = "LQA"
    techdoc = "techdoc"
    meetings = "meetings"
    verification = "verification"
    testcase = "testcase"
    qa_debt = "qa_debt"
    IgnoreLabels = IgnoreLabels


class Project:
    key: str = None
    name: str = None
    jira_id: str = None

    def __init__(self, key, name, jira_id, space, release_page_id, testops_id, testops_integration_id=4):
        self.key: str = key
        self.name = name
        self.jira_id = jira_id
        self.space = space
        self.release_page_id = release_page_id
        self.testops_id = testops_id
        self.testops_integration_id = testops_integration_id

    def __repr__(self) -> str:
        return str(self.key)

    def __str__(self):
        return str(self.key)


class Projects:
    MYPROJECT1 = Project(
        key="MYPROJECT1", name="MYSUBPROJECT1_NAME", jira_id="14307", space="PI", release_page_id=482974109, testops_id=63
    )
    MYPROJECT2 = Project(key="MYPROJECT2", name="MYSUBPROJECT2_NAME", jira_id="15154", space="MYPROJECT2", release_page_id=646523143, testops_id=70)
    MYPROJECT3 = Project(key="MYPROJECT3", name="MYSUBPROJECT3_NAME", jira_id="18700", space="MYPROJECT3", release_page_id=534388793, testops_id=840)
    MYPROJECT1 = MYPROJECT1.key
    MYPROJECT2 = MYPROJECT2.key
    MYPROJECT3 = MYPROJECT3.key
    any = [MYPROJECT2, MYPROJECT3, MYPROJECT1]


class Summaries:
    all = {
        TaskType.QA.verification: "Верификация",
        TaskType.QA.auto: "Создать/Обновить автотесты",
        TaskType.QA.manual: "Создать/Обновить ручные тест кейсы",
        TaskType.QA.load: "Провести НТ",
        TaskType.QA.demo: "Подготовить данные и провести демо",
        TaskType.DevOps.deploy_prod: "Установка в продуктивный контур релиза",
        TaskType.DevOps.deploy_stage: "Установка в stage контур релиза",
        TaskType.DevOps.deploy_prodlike: "Установка в prodlike контур релиза",
        TaskType.DevOps.resolve_session: "Провести сессию разрешения конфликтов в GQL схемах",
        TaskType.DevOps.mr_release_to_master: "Сделать MR из релизной ветки в master",
        TaskType.QA.release_verification: "Верификация релиза",
        TaskType.DevOps.migration: "Установить миграции в продуктивной среде для PostgreSQL/MongoDB",
        TaskType.Pm.check_tasks: "Убедиться что все задачи вошли в релиз",
        TaskType.TechDoc.release_notes: "Подготовить описание релиза",
        TaskType.QA.autotest_tag: "Установить тег для автотестов",
        TaskType.TechDoc.techdoc: "Создать/Обновить документацию",
    }
