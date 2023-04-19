from utils.manager_helpers.constants import Project, Projects
import requests


class ProdHelper:
    def __init__(self, project: Project):
        self.project = project

    def get_version(self) -> str | None:
        if self.project == Projects.MYPROJECT1:
            url = "https://localhost/version"
            response = requests.get(url, verify=False).json()
            version = response.get('version')
        else:
            raise NameError(f'Для проекта {self.project} нет реализации метода получения актуальной версии в проде.')
        return version
