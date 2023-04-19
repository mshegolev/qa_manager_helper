import datetime
import json
import os
import pathlib

import pandas as pd

from utils.manager_helpers.allure_helper import AllureHelper
from utils.manager_helpers.constants import Projects, Labels
from utils.manager_helpers.jira_helper import JiraHelper


class TraceablityCreator:
    def __init__(self, project=Projects.MYPROJECT1):
        self.project = project
        self.JiraHelper = JiraHelper(project=self.project)
        self.AllureHelper = AllureHelper(project=self.project)

    @staticmethod
    def save_to_file(issues, file_name=None):
        if file_name is None:
            file_name = datetime.datetime.now().strftime("%y-%m-%d_%H%M%S")
        with open(file_name, "w") as f:
            for i in issues:
                f.write(str(i))
        return file_name

    @staticmethod
    def read_file(file_name, type_if_file="issue"):
        path = "data/" + file_name
        data = pathlib.Path(pathlib.Path().cwd(), path).read_text()
        if type_if_file == "issue":
            data = json.loads(data)
        elif type_if_file == "case":
            data = json.loads(data)

        return data

    def update_cases_with_jira_issues(self):
        links = ["links", "issues"]
        cases = self.get_tests_from_allure()
        for case in cases:
            for link in links:
                if len(case.get(link)) > 0:
                    issues = case.get(link)
                    for issue in issues:
                        if not self.JiraHelper.is_parent_task(issue.get("name")):
                            parent_jira_key = self.JiraHelper.get_issue_parent_key(issue.get("name"))
                        else:
                            parent_jira_key = issue.get("name")
                        self.AllureHelper.add_issue(tc_id=case["id"], jira_key=parent_jira_key)
        return self

    def get_jira_issue_for_test(self, version=None) -> list:
        versions, jql_str = "", ""
        if version is None:
            versions = ",".join(self.JiraHelper.get_versions())
        elif isinstance(version, list):
            versions = ",".join(version)
        elif isinstance(version, str):
            versions = version
        elif isinstance(version, int):
            versions = str(version)

        jql_str = self.generate_query_get_jira_issues(versions)

        tasks = self.JiraHelper.get_issues_jql(jql_str=jql_str, maxResults=60)
        issues = [{"key": issue.key, "summary": issue.fields.summary} for issue in tasks]
        self.save_to_file(issues=issues)
        return issues

    def generate_query_get_jira_issues(self, versions=None) -> str:
        jql_str = ""
        if self.project == Projects.MYPROJECT1:
            jql_str = (
                'project = "MYSUBPROJECT1_NAME" AND type in (Story,Bug, Task, epic)'
                " AND (labels not in (%s,%s,%s) OR labels is EMPTY)" % Labels.IgnoreLabels.release,
                Labels.IgnoreLabels.noqa, Labels.IgnoreLabels.noQA,
            )
        elif self.project == Projects.MYPROJECT2:
            jql_str = 'project = "MYSUBPROJECT2_NAME" AND type = Story AND (labels is EMPTY OR labels !=noqa)'
        elif self.project == Projects.MYPROJECT3:
            jql_str = 'project ="MYSUBPROJECT3_NAME" AND type = Story AND (labels is EMPTY OR labels !=noqa)'
        if versions:
            jql_str += f" AND fixVersion in ({versions})"
        return jql_str

    def get_tests_from_allure(self):
        testcases = self.AllureHelper.get_testcases()
        i = 0
        for index, case in enumerate(testcases):
            print(f"{i} / {len(testcases)}")
            issues = self.AllureHelper.get_case_issues(case.get("id"))
            testcases[index]["issues"] = issues
            i += 1
        self.save_to_file(testcases)
        return testcases

    def create_trace_ablity_matrix(self, tasks=None, cases=None, raw_data_path=None):
        csv_file_name = ""
        if tasks is None and cases is None and raw_data_path is None:
            raise NameError("Укажите обязательные параметры либо raw_data, либо tasks и cases")
        elif tasks and cases:
            csv_file_name = self.generate_raw_data_file(cases, tasks)
        elif raw_data_path:
            if not os.path.isfile(raw_data_path):
                raise NameError(f"Укажите путь к корректному csv файлу:{raw_data_path}")
            csv_file_name = raw_data_path

        df1 = pd.read_csv(csv_file_name, delimiter=";")
        jira_total = df1.drop_duplicates("jira_id").shape[0]
        jira_with_cases = df1.drop_duplicates("jira_id").dropna().shape[0]
        jira_without_cases = jira_total - jira_with_cases
        test_case_coverage_percent = int(jira_with_cases * 100 / jira_total)

        coverage = {
            "jira_without_cases": [jira_without_cases],
            "jira_with_cases": [jira_with_cases],
            "jira_total": [jira_total],
            "test_case_coverage_percent": [test_case_coverage_percent],
        }
        df2 = pd.DataFrame(cases)
        df3 = pd.DataFrame(coverage)
        result_filename = datetime.datetime.now().strftime("%y-%m-%d-%H%M%S") + "_trace_ability_matrix.xlsx"
        with pd.ExcelWriter(result_filename) as writer:
            df1.to_excel(writer, sheet_name="issues")
            df2.to_excel(writer, sheet_name="cases")
            df3.to_excel(writer, sheet_name="coverage")
        print(f"Сформированный отчет доступен по ссылке {os.path.abspath(result_filename)}")
        return self

    def generate_raw_data_file(self, cases, tasks):
        lines = []
        target_links = "links"
        target_issue = "issues"
        delimiter = ";"
        for task in tasks:
            for case in cases:
                if case.get(target_links):
                    test_case_links = case.get(target_links)
                    print(task.get("key"), case.get(target_links))
                    for link in test_case_links:
                        if task.get("key") in link.get("url"):
                            _ = link.get("url")
                            line = self.line_generator(case, delimiter, task, target_links)
                            lines.append(line)
                elif case.get(target_issue):
                    test_case_links = case.get(target_issue)
                    print(task.get("key"), case.get(target_issue))
                    for link in test_case_links:
                        if task.get("key") in link.get("url"):
                            _ = link.get("url")
                            line = self.line_generator(case, delimiter, task, target_issue)
                            lines.append(line)
            is_task_in_cases = False
            for _ in lines:
                if task.get("key") in _:
                    is_task_in_cases = True
            if not is_task_in_cases:
                line = f"{delimiter}".join([task.get("key"), task.get("summary").replace(f"{delimiter}", ""), "", ""])
                lines.append(line)
        csv_file_name = "result.csv"
        with open(csv_file_name, "w+") as f:
            fields = "jira_id,jira_name,test_case_id,test_case_name,type_of_case\n".replace(",", delimiter)
            f.write(fields)
            for line in lines:
                f.write(line + "\n")
        return csv_file_name

    @staticmethod
    def line_generator(case, delimiter, task, type_of_issue):
        type_of_issue = "auto" if type_of_issue == "links" else "manual"
        line = f"{delimiter}".join(
            [
                task.get("key"),
                task.get("summary").replace(f"{delimiter}", ""),
                str(case.get("id")),
                str(case.get("name").replace(f"{delimiter}", "")),
                str(type_of_issue),
            ]
        )
        return line
