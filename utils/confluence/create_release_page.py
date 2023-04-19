from utils.confluence.confluence_helper import ConfluenceHelper
from utils.manager_helpers.constants import Projects

project = Projects.MYPROJECT2
fix_version = "v1.0.0"

if __name__ == "__main__":
    confluence = ConfluenceHelper(project=project)
    confluence.create_release_page(fix_version=fix_version)
