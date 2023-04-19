import json

import requests

from utils.constants import ALLURE_SERVICES_URL, HTTPS_JIRA_URL
from utils.manager_helpers.constants import Project, Projects


class AllureHelper:
    def __init__(self, host=ALLURE_SERVICES_URL, project=Projects.MYPROJECT1, token=None):
        self.host = host
        if isinstance(project, str):
            self.project = getattr(Projects, project.upper())
        elif isinstance(project, Project):
            self.project = project
        self.project_id = self.project.testops_id
        self.base_url = ALLURE_SERVICES_URL + "/api/rs"
        if token is None:
            self.token = 'change_me'

        else:
            self.token = token
        self.headers = {
            "accept": "*/*",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Authorization": "Api-Token " + self.token,
        }

        self.verify = False
        self.requests = requests

    def get_testcases(self, maxsize=6) -> list:
        payload = {"projectId": self.project_id, "rql": "true", "page": 0, "size": maxsize}
        path = "/testcase/__search"
        url = self.base_url + path
        response = self.requests.get(url=url, headers=self.headers, params=payload, verify=self.verify).json()
        result = response.get("content")
        return result

    def get_case_issues(self, tc_id):
        path = f"/testcase/{tc_id}/issue"
        url = self.base_url + path
        result = self.requests.get(url=url, headers=self.headers, verify=self.verify)
        result = result.json()
        return result

    def get_test_case(self, tc_id):
        path = "/testcase/%s" % tc_id
        url = self.base_url + path
        result = self.requests.get(url=url, headers=self.headers, verify=self.verify)
        result = result.json()
        return result

    def add_issue(self, tc_id, jira_key):
        path = f"/testcase/{tc_id}/issue"
        url = self.base_url + path

        issues = self.get_case_issues(tc_id=tc_id)
        if issues:
            for issue in issues:
                if jira_key == issue.get("name"):
                    return True

        issue = {
            "integrationId": self.project.testops_integration_id,
            "name": jira_key,
            "url": HTTPS_JIRA_URL + "/browse/%s" % jira_key,
            "closed": False,
        }
        issues.append(issue)
        payload = json.dumps(issues)
        result = self.requests.post(url=url, data=payload, headers=self.headers, verify=self.verify)
        result = result.json()
        return result

    def add_link(self, tc_id, jira_key, link_type=None):
        issues = []
        if link_type is None:
            link_type = "links"
        path = "/testcase/%s" % tc_id
        url = self.base_url + path
        case = self.get_test_case(tc_id=tc_id)
        tasks = case.get(link_type)
        if tasks:
            for task in tasks:
                if jira_key == task.get("name"):
                    return True
        issue = {
            "integrationId": self.project.testops_integration_id,
            "name": jira_key,
            "url": HTTPS_JIRA_URL + "/browse/%s" % jira_key,
            "closed": False,
        }
        issues.append(issue)
        payload = {"links": issues}
        payload = json.dumps(payload)
        response = self.requests.patch(url=url, data=payload, headers=self.headers, verify=self.verify)
        return response.json()
