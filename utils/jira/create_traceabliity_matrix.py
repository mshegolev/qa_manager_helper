import urllib3

from utils.manager_helpers.constants import Projects
from utils.manager_helpers.traceability_helper import TraceablityCreator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    # fixversion = "v1.0.0"
    project = Projects.MYPROJECT1
    tc = TraceablityCreator(project=project)
    # tc.update_cases_with_jira_issues()
    issues = tc.get_jira_issue_for_test()
    cases = tc.get_tests_from_allure()
    tc.create_trace_ablity_matrix(tasks=issues, cases=cases)
