import re

from atlassian import Confluence

from utils.confluence.templates import CONFLUENCE_RELEASE_TEMPLATES, PARENT_TITLE_RELEASES, PERFORMANCE_RELEASE_TEMPLATE
from utils.constants import HTTPS_CONFLUENCE_URL, HTTPS_JIRA_URL
from utils.jira import JIRA_PASSWORD, JIRA_USER
from utils.manager_helpers.constants import Project
from utils.manager_helpers.issue_types import IssueTypes
from utils.manager_helpers.jira_helper import JiraHelper


class ConfluenceHelper:
    def __init__(self, project: Project):
        assert isinstance(project, Project)
        self.project = project
        self.project_name = project.name
        self.space = project.space

        self.JiraHelper = JiraHelper(project=self.project)
        self._confluence = Confluence(
            url=HTTPS_CONFLUENCE_URL, username=JIRA_USER, password=JIRA_PASSWORD, verify_ssl=False, kerberos={}
        )
        # if fix_version is None:
        #     self.fix_version = self.JiraHelper.get_versions()[-2]

    def generate_release_page(self, fix_version=None):
        if fix_version is None:
            fix_version = self.fix_version
        qa_task = self.generate_qa_task_section(fix_version)
        goals = self.generate_goals_section(fix_version)
        release_content = self.generate_issues_section(fix_version)

        template = CONFLUENCE_RELEASE_TEMPLATES.get(self.project.key)

        content = (
            template.replace(r"${fix_version}", fix_version)
            .replace(r"${goals}", goals)
            .replace("${qa_verification_task}", qa_task)
            .replace(r"${release_content}", release_content)
            .replace(r"${project}", self.project.key)
        )

        return content

    def generate_issues_section(self, fix_version, contents=""):
        errors_section = "<h2>9.1. Исправленные ошибки</h2>"
        story_section = "<h2>9.2. Сделанные истории</h2>"
        is_bug_section_exists = False
        if not contents:
            issues = self.JiraHelper.get_issues_release_notes(fix_version_name=fix_version)
            for issue in issues:
                if int(issue.fields.issuetype.id) in [IssueTypes(project=self.project_name).bug_id]:
                    errors_section += self.create_li_string(issue)
                    is_bug_section_exists = True
                else:
                    story_section += self.create_li_string(issue)
            if not is_bug_section_exists:
                errors_section += "<p>нет</p>"
            contents = errors_section + story_section
        return contents

    @staticmethod
    def create_li_string(issue):
        url = HTTPS_JIRA_URL + "/browse/" + str(issue.key)
        key = issue.key
        name = issue.fields.summary
        return f"""<li>[<a href="{url}">{key}</a>]<span> </span>{name}</li>"""

    def generate_qa_task_section(self, fix_version):
        qa_task = self.JiraHelper.get_qa_verification_task(fix_version=fix_version)
        url = self.JiraHelper.jira_options.get("server") + "/browse/" + qa_task.key
        key = qa_task.key
        qa_verification_task = f"""<a href="{url}">{key}</a>"""
        return qa_verification_task

    def get_fix_versions(self):
        return self.JiraHelper.get_versions()

    def create_release_page(self, fix_version, space=None, title=None, body=None, parent_page_id=None):
        # assert fix_version in self.get_fix_versions()
        if space is None:
            space = self.space
        if title is None:
            title = f"Релиз {self.project.key.upper()} {fix_version}"
        if body is None:
            body = self.generate_release_page(fix_version=fix_version)
        if parent_page_id is None:
            parent_page_id = self._confluence.get_page_id(space, PARENT_TITLE_RELEASES)
        assert parent_page_id is not None, "Создайте главную страницу Релизы в проекте"
        release_page = self._confluence.update_or_create(parent_id=parent_page_id, title=title, body=body)
        assert release_page, "Что-то пошло не так, станица не создана"
        url = release_page.get("_links").get("base") + release_page.get("_links").get("webui")
        print(url)
        return self

    def get_page_id(self, title):
        return self._confluence.get_page_id(self.space, title)

    def get_release_page_link(self, fix_version):
        title = f"Релиз {self.project.key.upper()} {fix_version}"
        page_id = self._confluence.get_page_id(self.space, title)
        if page_id:
            link = HTTPS_CONFLUENCE_URL + '/pages/viewpage.action?pageId=%s' % page_id
        else:
            raise NameError('Страница с релизом не найдена! Создайте страницу.')
        return link

    def get_goal_raw_description(self, fix_version):
        version = self.JiraHelper._jira.get_project_version_by_name(self.project.key, fix_version)
        return version.description

    def generate_goals_section(self, fix_version):
        result = ""
        pattern = self.project_name + r"-\d+"
        description = self.get_goal_raw_description(fix_version=fix_version)

        issues = re.findall(pattern, description)
        if issues:
            for issue in issues:
                _ = self.JiraHelper.get_issue(issue)
                key = _.key
                name = _.fields.summary
                url = self.JiraHelper._jira.server_url + "/browse/" + key
                result += f"""<li>[<a href="{url}">{key}</a>]<span> </span>{name}</li>"""
        else:
            result = description

        return result

    def create_load_page(self, title):
        page_id = self.get_page_id(self.project.space, title)
        PARENT_TITLE_RELEASES = "QA - Отчет о НТ"

        if page_id is None:
            body = self.generate_load_page()

            parent_page_id = self._confluence.get_page_id(self.project.space, PARENT_TITLE_RELEASES)
            assert parent_page_id is not None, "Создайте главную страницу для отчетов по тестированию"
            release_page = self._confluence.update_or_create(parent_id=parent_page_id, title=title, body=body)
            assert release_page, "Что-то пошло не так, станица не создана"
            url = release_page.get("_links").get("base") + release_page.get("_links").get("webui")
            print(url)
        return url

    @staticmethod
    def generate_load_page():
        template = PERFORMANCE_RELEASE_TEMPLATE
        return template
