import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask_mail import Mail, Message

env = Environment(
        loader=FileSystemLoader(searchpath="./"),
        autoescape=select_autoescape(['html', 'xml'])
    )

def create_verification_email(username, email, link):
    subject = "Verification"
    template = env.get_template("templates/verification_email.html")
    html_content = template.render(subject=subject, 
                                   link = link,
                                   username = username,)

    msg = Message("New Test",
                  recipients=[email],
                  sender="william.matthew.murray@gmail.com")
    msg.html = html_content
    return msg