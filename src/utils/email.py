import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import markdown
from typing import Dict

logger = logging.getLogger(__name__)

class EmailUtil:
    def __init__(self, config: Dict):
        self.config = config
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.recipients = os.getenv("RECIPIENT_EMAILS", "").split(",")

    def send_email(self, content_markdown: str):
        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not found. Skipping email sending.")
            print("=== DRY RUN: Email Content ===")
            print(content_markdown)
            print("============================")
            return

        try:
            # Convert Markdown to HTML
            html_content = markdown.markdown(content_markdown)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Daily AI Papers - {self.config.get('agent', {}).get('name', 'Agent')}"
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(self.recipients)

            # Attach parts
            part1 = MIMEText(content_markdown, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)

            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipients, msg.as_string())
            
            logger.info(f"Email sent to {len(self.recipients)} recipients.")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
