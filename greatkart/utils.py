from django.conf import settings

import smtplib
from email.message import EmailMessage as RawEmailMessage

def send_email(subject, body, to_emails):
    from django.conf import settings
    # Configuration
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    sender_email = settings.DEFAULT_FROM_EMAIL
    auth_sender_email = settings.EMAIL_HOST_USER
    auth_sender_password = settings.EMAIL_HOST_PASSWORD

    msg = RawEmailMessage()
    msg.set_content(body)
    msg.add_alternative(body, subtype='html')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_emails

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(1)  # <--- important
            # comment the below 2 in Production server
            #server.starttls()
            #server.login(auth_sender_email, auth_sender_email)
            result = server.send_message(msg)
            print(f"Email sent successfully! : {result}")
        return True
    except Exception as e:
        print(f"Error sending email! : {e}")
        return False


def gst_breakup(amount_with_gst, cgst_percent, sgst_percent):
    total_gst_percent = cgst_percent + sgst_percent

    amount_without_gst = amount_with_gst / (1 + total_gst_percent / 100)
    cgst_amount = amount_without_gst * cgst_percent / 100
    sgst_amount = amount_without_gst * sgst_percent / 100

    return (
        round(amount_without_gst, 2),
        round(cgst_amount, 2),
        round(sgst_amount, 2),
    )