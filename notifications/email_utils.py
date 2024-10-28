from django.conf import settings
from sendgrid.helpers.mail import Mail


def send_email(subject: str, message: str, to_email: str):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=message
    )

    try:
        sg = settings.SENDGRID_CLIENT
        sg.send(message)
    except Exception as e:
        print(f"An error occurred while sending email to {to_email}. {e}")
