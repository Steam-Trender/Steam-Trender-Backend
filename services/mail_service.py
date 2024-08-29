import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
from app.settings import settings


class MailService:
    @staticmethod
    def get_message_template(topic: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["From"] = settings.MAIL_USER
        msg["To"] = settings.MAIL_RECEIVER
        msg["Subject"] = f"[STEAM TRENDER] {topic}"
        return msg

    @staticmethod
    def send_message(msg: MIMEMultipart) -> None:
        try:
            with smtplib.SMTP(settings.MAIL_SERVER, 587) as server:
                server.starttls()
                server.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError as e:
            print(f"Authentication failed: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def send_alert_up(self) -> None:
        msg = self.get_message_template(topic="up")

        text = "SteamTrender is up."
        msg_text = MIMEText(text, "plain")
        msg.attach(msg_text)

        self.send_message(msg)

    def send_alert_report(self, filename: str) -> None:
        with open(f"{config.DATA_FOLDER}/{filename}.json", "rb") as file:
            file_content = file.read()

        msg = self.get_message_template(topic=filename)

        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(file_content)
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition", f"attachment; filename={filename}.json"
        )
        msg.attach(attachment)

        self.send_message(msg)


mail_service = MailService()
