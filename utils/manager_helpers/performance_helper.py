from utils.confluence.confluence_helper import ConfluenceHelper
from utils.constants import HTTPS_CONFLUENCE_URL
from utils.manager_helpers.constants import Project
from utils.manager_helpers.mail_helper import MailHelper
from utils.manager_helpers.prod_helper import ProdHelper


class PerformanceHelper:
    def __init__(self, project: Project):
        self.project = project
        self.mailer = MailHelper()
        self.confluence = ConfluenceHelper(project=self.project)
        self.prod = ProdHelper(project=project)

    def send_initial_plan(self, subject, profile, page_url, start_date, start_time, end_date, end_time, goal=None,
                          current_version=None):
        email_address = 'user1@r.ru;user2@r.ru'
        if current_version is None:
            current_version = self.prod.get_version()
        if subject is None:
            subject = "[НТ]Провести нагрузочное тестирование MYSUBPROJECT1 2100 RPS"
        if goal is None:
            goal = 'Какую нагрузку держит MYSUBPROJECT1_NAME в зонтичной реализации MYSUBPROJECT1 целевое 201000 RPS'
        msg = f"Всем привет!\n" \
              f"Мы хотим провести НТ в продуктивной среде. Текущая версия MP1 {current_version}" \
              f"Целью испытания является определить:\n " \
              f"{goal}\n" \
              f" Будем проводить проверку с профилем {profile}, " \
              f"описание профилей > {HTTPS_CONFLUENCE_URL}+/pages/viewpage.action?pageId=123\n" \
              f"Время проведения испытаний: {start_date} с {start_time} по {end_date} {end_time} (+3 UTC)\n" \
              f"Методика испытаний {page_url}\n" \
              f"Прошу завести RFC"
        print(email_address)
        print(subject)
        print(msg)
        # assert self.mailer.send_email(subject=subject, message=msg, email_address=email_address)
        pass

    def create_load_page(self, title):
        return self.confluence.create_load_page(title)
