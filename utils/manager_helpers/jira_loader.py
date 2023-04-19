import json
import logging
import time

from utils.manager_helpers.constants import Labels, Projects
from utils.manager_helpers.jira_helper import JiraHelper
from utils.manager_helpers.sqlite3_helper import Sqlite3Helper

ONE_MINUTE = 60


class JiraLoader(JiraHelper):
    def __init__(self, project=Projects.MYPROJECT1, db_name=None, db_path=None):
        super().__init__(project=project)
        self.project = project
        self.sqlite = Sqlite3Helper(db_path=db_path, db_name=db_name)

    def load_only_raw(self, db_name=None, keys=list()):
        columns = ["raw"]
        db_name = self.sqlite.create_table(table_name=db_name, columns=columns)
        if keys:
            while keys:
                issues = [self.get_issue(keys.pop())]
        else:
            issues = self.get_all_issues()
        for issue in issues:
            logging.info(f"Загрузка  сырых данных для {issue.key}")
            self.sqlite.insert_issue(issue)
        logging.info(f"Все задачи были скопированы в БД {db_name}")
        return self

    def load_data(self, db_name=None):
        columns = self.get_jira_columns()
        db_name = self.sqlite.create_table(table_name=db_name, columns=columns)
        # issues = self.get_all_issues()
        issues = [self.get_issue("MYPROJECT1-1213"), self.get_issue("MYPROJECT1-1816")]

        if len(issues) == 0:
            raise "Нет Jira issues"
        for issue in issues:
            self.sqlite.insert_issue(issue)
        logging.info(f"Все задачи были скопированы в БД {db_name}")
        return self

    def get_jira_columns(self):
        jql_str = f'project = "{self.project.name}"'
        issues = self.get_issues_jql(jql_str=jql_str, maxResults=1, startAt=0)
        columns = [field for field in dir(issues[0]) if not field.startswith("_")]
        columns += [field for field in dir(issues[0].fields) if not field.startswith("_")]
        return columns

    def get_issues_with_work_log(self):
        worklogs = []
        issues = self.get_all_issues(fields=["key", "summary", "labels"])
        for issue in issues:
            logging.info(f"Получить worklog по задача {issue.key}")
            print(f"Получить worklog по задача {issue.key}")
            worklogs.append({issue: self._jira.worklogs(issue)})
        return worklogs

    def get_qa_velocity_raws(self) -> list:
        issues = self.get_issues_with_work_log()
        lines = []
        for issue in issues:
            k = list(issue.keys())[0]
            logging.info(f"Определить тип задачи {k.key}")
            work_type = self.choose_work_type(labels=k.fields.labels)
            if len(list(issue.values())[0]) > 0:
                for wl in list(issue.values())[0]:
                    lines.append(
                        {
                            "key": k.key,
                            "summary": k.fields.summary,
                            "labels": json.dumps(k.fields.labels),
                            "key_id": wl.issueId,
                            "wl_id": wl.jira_id,
                            "author_name": wl.author.name,
                            "started": wl.started,
                            "timeSpentSeconds": wl.timeSpentSeconds,
                            "work_type": work_type,
                        }
                    )
            else:
                lines.append(
                    {
                        "key": k.key,
                        "summary": k.fields.summary,
                        "labels": json.dumps(k.fields.labels),
                        "key_id": None,
                        "wl_id": None,
                        "author_name": None,
                        "started": None,
                        "timeSpentSeconds": None,
                        "work_type": work_type,
                    }
                )

        return lines

    def get_worklog(self, issue):
        return self._jira.worklogs(issue)

    def get_all_issues(self, timeout=5 * ONE_MINUTE, fetch=500, fields=None):
        jql_str = f'project = "{self.project.name}"'
        issues = []
        all_page_loaded = False
        startAt = 0
        timeout += time.time()
        total = self.get_issues_jql(jql_str=jql_str, maxResults=1, startAt=0, fields=fields).total
        print(f"Начинаем загрузку из jira, всего задач {total}")
        while not all_page_loaded and time.time() < timeout:
            logging.info(f"Получить задачи из jira c {startAt} до {startAt + fetch}")
            print(f"Получить задачи из jira c {startAt} до {startAt + fetch}")
            _ = self.get_issues_jql(jql_str=jql_str, maxResults=fetch, startAt=startAt, fields=fields)
            issues += _
            logging.info(f"Загрузили {len(_)}")
            startAt += fetch
            if len(_) == 0:
                all_page_loaded = True
        assert total == len(issues), f"Не все задачи загрузились: загрузилось {len(issues)} из {total}"
        return issues

    def create_worklog_tbl(self, db_path, db_name):
        columns = ["key", "worklog"]
        self.sqlite.create_table(columns=columns, db_path=db_path, table_name=db_name)
        return self

    def create_qa_velocity_tbl(self, issues: list, db_path, table_name):
        columns = issues[0].keys()
        self.sqlite.create_table(columns=columns, db_path=db_path, table_name=table_name)

        for issue in issues:
            print(f"Записать значение в базу данных {issue}")
            self.sqlite.insert_issue(issue)

        return self

    def get_worklog_section(self):
        # todo: get worklogs from db  like list
        # self.sqlite
        query = (
            "SELECT pk,json_extract(big.raw,'$.key') AS key, "
            "json_extract(big.raw,'$.fields.worklog.worklogs') AS worklogs "
            "FROM MYPROJECT1_jira AS big WHERE json_array_length(big.raw,'$.fields.worklog.worklogs')"
        )
        result = self.sqlite.select(query=query)
        return result

    def choose_work_type(self, issue=None, labels=None) -> str:
        if issue is None and labels is None:
            work_type = "unknown"
        elif issue:
            issue = self.get_issue(issue)
            work_type = json.dumps(
                list(
                    set([_ for _ in dir(Labels) if not _.startswith("_")]).intersection(
                        [_.lower() for _ in issue.fields.labels]
                    )
                )
            )

        elif labels:
            work_type = json.dumps(
                list(set([_ for _ in dir(Labels) if not _.startswith("_")]).intersection([_.lower() for _ in labels]))
            )
        else:
            work_type = "unknown"
        logging.info(f"Тип задачи определен как {work_type}")
        print(f"Тип задачи определен как {work_type}")
        return work_type
