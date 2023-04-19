import json
import uuid

from utils.manager_helpers.constants import Projects
from utils.manager_helpers.jira_loader import JiraLoader


def load_data_for_all_projects():
    projects = [Projects.MYPROJECT1, Projects.MYPROJECT3, Projects.MYPROJECT2]
    for project in projects:
        db_name = project.key + "_jira"
        path = "230411_raw_jira.db"
        keys = []
        loader = JiraLoader(project=project, db_name=db_name, db_path=path)
        data = loader.load_only_raw(db_name=db_name, keys=keys)
        print("Данные загружены успешно? ", len(data) > 0)


def create_worklog_tbl(project, db_name=None, db_path=None):
    if db_name is None:
        db_name = project.key + "worklog"
    if db_path is None:
        db_path = "230411_raw_jira.db"
    loader = JiraLoader(project=project, db_path=db_path, db_name=db_name)
    loader.create_worklog_tbl(db_path=db_path, db_name=db_name)
    issues = loader.get_worklog_section()
    # todo: get wls
    # get from wl createat date, author, and timespant
    # save this from new tbl prj-name-worklogs
    # next action create select from prj-name-worklogs with group by createat.
    #
    columns = ["pk", "uuid", "key", "worklog"]
    for issue in issues:
        wls = json.loads(issue[2])
        for wl in wls:
            pk = None
            uniq_uuid = str(uuid.uuid4())
            key = issue[1]
            worklog = json.dumps(wl)
            cols = ",".join(["'" + _ + "'" for _ in columns])
            vals = str("?," * len(columns)).removesuffix(",")
            query = f"INSERT INTO '{db_name}' ({cols}) VALUES ({vals})"
            values = [pk, uniq_uuid, key, worklog]
            loader.sqlite.insert(query=query, values=values)
            print(wl)


def create_qa_velocity_tbl(project, table_name=None, db_path=None):
    if table_name is None:
        table_name = project.key.lower() + "_qa_velocity"
    if db_path is None:
        db_path = "230411_raw_jira.db"
    loader = JiraLoader(project=project, db_path=db_path, db_name=table_name)
    issues = loader.get_qa_velocity_raws()
    loader.create_qa_velocity_tbl(issues, db_path=db_path, table_name=table_name)


if __name__ == "__main__":
    # load_data_for_all_projects()
    project = Projects.MYPROJECT1
    db_name = project.key.lower() + "_worklog"
    db_path = "230411_raw_jira.db"
    # loader = JiraLoader(project=project, db_name=db_name, db_path=db_path)
    # keys = ['MYPROJECT1-464']
    # data = loader.load_only_raw(db_name=db_name, keys=keys)

    # create_worklog_tbl(project=project, db_path=db_path, db_name=db_name)
    create_qa_velocity_tbl(project=project, db_path=db_path)
    print("Done")
