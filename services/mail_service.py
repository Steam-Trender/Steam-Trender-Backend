import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from app.settings import settings


class MailService:
    @staticmethod
    def send_data(filename: str) -> None:
        with open(f"data/{filename}", "rb") as file:
            file_content = file.read()

        msg = MIMEMultipart()
        msg["From"] = settings.MAIL_USER
        msg["To"] = settings.MAIL_RECEIVER
        msg["Subject"] = f"[STEAM TRENDER] {filename}"

        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(file_content)
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(attachment)

        try:
            with smtplib.SMTP(settings.MAIL_SERVER, 587) as server:
                server.starttls()
                server.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError as e:
            print(f"Authentication failed: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


mail_service = MailService()