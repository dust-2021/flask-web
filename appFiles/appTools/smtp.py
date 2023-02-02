import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
import os


class Smtp:

    allowed_mail = []

    def __init__(self, email_addr, email_pw, smtp_server_host):
        self.email_addr = email_addr
        self.email_pw = email_pw
        self.smtp_server_host = smtp_server_host
        self.server = None

    @staticmethod
    def addr_formatter(addr: str):
        addr_name, addr_ = parseaddr(addr)
        return formataddr((Header(addr_name, 'utf-8').encode(), addr_))

    def login(self):
        self.email_addr = os.getenv('email_addr')
        self.email_pw = os.getenv('email_password')
        self.server = smtplib.SMTP_SSL(self.smtp_server_host.split('@')[0], 465)
        self.server.login(self.email_addr, self.email_pw)

    def send_email(self, msg: str, title: str, target: list):
        Msg = MIMEText(msg, 'html', 'utf-8')
        Msg['From'] = self.addr_formatter(self.email_addr)
        Msg['Subject'] = Header(title, 'utf-8').encode()
        Msg['TO'] = ','.join(target)
        self.login()
        self.server.sendmail(self.email_addr, target, Msg.as_string())
        self.server.quit()
