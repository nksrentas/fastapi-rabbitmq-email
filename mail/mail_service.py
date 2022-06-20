from enum import Enum
import os
from typing import List

from mail.send_grid import SendGridProvide


class MailServiceProvider(Enum):
    SEND_GRID = "SendGrid"


class MailService:
    """
    Class that send emails with the help of various email providers
    """

    def __init__(self, provider: MailServiceProvider = None) -> None:
        try:
            self.provider = os.environ.get("EMAIL_PROVIDER") or provider or MailServiceProvider.SEND_GRID
        except Exception as e:
            raise e

    def send_email(
        self,
        from_email: str,
        to_emails: List[str],
        subject: str,
        txt_body: str,
        html_body: str,
        attachments: List[any],
    ) -> None:
        """
        Send an email with the help of the provider
        """
        if self.provider == MailServiceProvider.SEND_GRID:
            send_grid = SendGridProvide(os.environ.get("SENDGRID_API_KEY"))
            send_grid.send_email(
                from_email, to_emails, subject, txt_body, html_body, attachments
            )
        else:
            raise NotImplementedError("Provider not implemented")

    def mock_send_email(self):
        """
        Mock function to send an email
        """
        print('Mock email sent')

mail_service = MailService()