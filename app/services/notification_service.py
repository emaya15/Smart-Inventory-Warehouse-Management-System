import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from sqlalchemy.orm import Session
from app.database import settings, SessionLocal
from app.models.notification import Notification

logger = logging.getLogger(__name__)

def send_email_background(recipient_email: str, subject: str, body: str):
    db: Session = SessionLocal()
    status = "SENT"
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        if settings.SMTP_HOST and settings.SMTP_USERNAME != "user@example.com":
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            logger.info(f"Simulating email dispatch to {recipient_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        status = "FAILED"
    finally:
        notification = Notification(
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            status=status
        )
        db.add(notification)
        db.commit()
        db.close()
