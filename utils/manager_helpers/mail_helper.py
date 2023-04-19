from exchangelib import Account, Credentials, Mailbox, Message
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

from utils.jira import JIRA_PASSWORD, JIRA_USER

BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter


class MailHelper:
    def __init__(self, user=JIRA_USER, password=JIRA_PASSWORD):
        global sender
        self.credentials = Credentials(username=user, password=password)
        if not user.endswith("@r.ru"):
            sender = user + "@r.ru"
        self.account = Account(sender, credentials=self.credentials, autodiscover=True)

    def send_email(self, subject: str, message: str, email_address="qa_manager_login@r.ru") -> bool:
        m = Message(
            account=self.account,
            folder=self.account.sent,
            subject=subject,
            body=message,
            to_recipients=[Mailbox(email_address=email_address)],
        )
        return m.send_and_save()

    def is_email_exist(self, subject, message, email_address):
        self.account.root.refresh()
        for item in self.account.inbox.all().order_by("-datetime_received")[:500]:
            if item.subject and subject in item.subject:
                if message in item.text_body and email_address in item.sender:
                    print(item.subject, item.sender, item.datetime_received)
