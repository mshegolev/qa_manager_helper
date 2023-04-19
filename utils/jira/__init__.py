import os

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
JIRA_USER = os.environ.get("JIRA_LOGIN")
JIRA_PASSWORD = os.environ.get("JIRA_PASSWORD")
key = None
just_do_it = None
