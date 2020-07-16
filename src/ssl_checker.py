import socket
import ssl
import re,sys,os,datetime
import config
import site_config
from email_service import EmailService

def ssl_expiry_date(domainname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=domainname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)
    conn.connect((domainname, 443))
    ssl_info = conn.getpeercert()
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt).date()

def ssl_valid_time_remaining(domainname):
    """Number of days left."""
    expires = ssl_expiry_date(domainname)
    return expires - datetime.datetime.utcnow().date()
    
def check(url):
    try:
        expDate = ssl_valid_time_remaining(url)
        (a, b) = str(expDate).split(',')
        (c, d) = a.split(' ')
    except:
        return (-1, 'ERROR')
    status = ''
    days = int(c)
    if days < 10:
        status = 'Critial'
    elif days >=10 and days < 20:
        status = 'Warning'
    else:
        status = 'OK'
    return (days,status)

def send_mail(recipients,title,content,config):
    email = EmailService()
    email.init(config.SMTP_SERVER,port=config.SMTP_PORT, tls=config.SMTP_TLS, ssl=config.SMTP_SSL)
    email.authenticate(config.SMTP_USER, config.SMTP_PASS)
    email.set_message(
        from_address=config.FROM_ADDRESS,
        to_address=recipients,
        subject=title,
        content=content, 
        content_type='html',
        from_display_name=config.FROM_DISPLAY_NAME, 
        )
    email.send()
    return

def handler(event, context):
    sites = site_config.SITE_LIST
    send = False
    line_template = '<p>{status}:Site {site}, {days} days left to expire.</p>\n'
    content = ''
    for site in sites:
        days, status = check(site)
        if days < config.NOTIFICATION_THRESHOLD:
            send = True
        days = str(days)
        content += line_template.format(site=site, days=days, status=status)
    print(content)
    if send:
        send_mail(config.NOTIFICATION_EMAIL,'SSL Checker - Attention','<html><body>{content}</body></html>'.format(content=content),config)
    return

handler({},{})