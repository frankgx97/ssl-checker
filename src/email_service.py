import smtplib
from email.mime.text import MIMEText
from email_interface import EmailServiceInterface

class EmailService(EmailServiceInterface):
    def __init__(self):
        super().__init__()

    def init(self, hostname:str, port:int, ssl:bool=False, tls:bool=False):
        '''
        Initiate a smtp instance

        :param hostname: string, hostname of the smtp server.
        :param port: int, the port number of the smtp server.
        :param ssl: bool, true if the smtp server requires ssl.
        :param tls: bool, true if the smtp server requires tls.
        :return: None
        '''
        self.__hostname = hostname
        self.__port = port
        self.__ssl = ssl
        self.__tls = tls

        if ssl and tls:
            raise Exception('SSL and TLS cannot be both on')

        if ssl:
            self.__smtp = smtplib.SMTP_SSL(host=hostname, port=port)
        else:
            self.__smtp = smtplib.SMTP(hostname, port=port)
        if tls:
            self.__smtp.ehlo()
            self.__smtp.starttls()
            self.__smtp.ehlo()
        return

    def authenticate(self, username:str, password:str):
        '''
        Log into smtp server if the server requires authentication

        :param username: string, username of smtp server
        :param password: string, password of the smtp server
        :return: None
        '''
        if not self.__smtp:
            raise Exception('SMTP instance not initialized.')
        self.__smtp.login(username, password)
        return
    
    def set_message(self, from_address:str, to_address:[str], subject:str, content:str, cc:[str]=[], bcc:[str]=[], content_type:str='plain', from_display_name:str=None):
        '''
        Set attributes for the email message

        :param from_address: From address
        :param to_address: To address
        :param subject: Subject
        :param content: Content
        :param cc: cc, Optional
        :param bcc: bcc, Optional
        :param content_type: Content type for encoding email content, can be plain/html, Optional
        :param from_display_name: Display name from sender, Optional
        '''
        self.__from_address = from_address
        self.__to_address = to_address
        self.__subject = subject
        self.__content = content
        self.__cc = cc
        self.__bcc = bcc
        self.__all_recipients_address = to_address + cc + bcc

        if content_type not in ['plain','html']:
            raise Exception('Invalid content_type, must be plain or html.')

        self.__mime_msg = MIMEText(content, content_type)
        self.__mime_msg['Subject'] = subject
        self.__mime_msg['From'] = '{name} <{address}>'.format(name=from_display_name, address=from_address) if from_display_name else from_address
        self.__mime_msg['To'] = ', '.join(to_address)
        if cc:
            self.__mime_msg['Cc'] = ', '.join(cc)
        return
    
    def send(self):
        '''
        Send email
        '''
        self.__smtp.set_debuglevel(1)
        if not self.__smtp:
            raise Exception('SMTP instance not initialized.')
        self.__smtp.set_debuglevel(1)
        self.__smtp.sendmail(self.__from_address, self.__all_recipients_address, self.__mime_msg.as_string())
        self.__smtp.quit()
        return