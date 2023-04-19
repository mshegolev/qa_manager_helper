from utils.constants import HTTPS_CONFLUENCE_URL
from utils.manager_helpers.constants import Projects
from utils.manager_helpers.performance_helper import PerformanceHelper

if __name__ == "__main__":
    project = Projects.MYPROJECT1
    title = f"НТ - 2033-04-19"

    send_planning_mail = True
    start_test = False
    end_test = False
    create_report = False

    if send_planning_mail:
        performance = PerformanceHelper(project=project)
        subject = "[НТ]Провести нагрузочное тестирование MYSUBPROJECT1 26 RPS"
        profile = '1,2'
        page_url = HTTPS_CONFLUENCE_URL+'/pages/viewpage.action?pageId=123'
        start_date = '20.04.2033'
        start_time = '00:00'
        end_date = '20.04.2033'
        end_time = '24:00'
        performance.send_initial_plan(subject=subject, profile=profile, page_url=page_url, start_date=start_date,
                                      start_time=start_time, end_date=end_date, end_time=end_time)
