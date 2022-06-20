import sendgrid
from sendgrid.helpers.mail import *
from typing import List

from exceptions import ConstructEmail


class SendGridProvide:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)

    def __build_message(
        self,
        from_email: str,
        to_emails: List[str],
        subject: str,
        txt_body: str,
        html_body: str,
        attachments: List[any],
    ) -> Mail:
        try:
            message = Mail()

            message.from_email(from_email=from_email)
            message.add_to(to_email=to_emails)
            message.subject(subject=subject)
            message.add_content(
                content=Content(type="text/plain", value=txt_body)
            ) 
            message.add_content(
                content=Content(type="text/html", value=html_body)
            )
            message.attachments(attachments=attachments)
            

            return message
        except ValueError:
            raise ConstructEmail("Some error message")

    def send_email(
        self,
        from_email: str,
        to_emails: List[str],
        subject: str,
        txt_body: str,
        html_body: str,
        attachments: List[any],
    ) -> None:
        try:
            message = self.__build_message(
                from_email=from_email,
                to_emails=to_emails,
                subject=subject,
                txt_body=txt_body,
                html_body=html_body,
                attachments=attachments,
            )

            response = self.sg.client.mail.send(message)

            return response.status_code
        except Exception as e:
            pass
