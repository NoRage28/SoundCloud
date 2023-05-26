from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from rest_framework.request import Request
from users.tokens import account_token_generator
from users.models import User

from typing import Dict, Any


class EmailSender:
    @staticmethod
    def send_email(mail_subject: str, message: Dict[str, Any], to_email: str) -> bool:
        email = EmailMessage(subject=mail_subject, body=message, to=[to_email])
        if email.send():
            return True
        return False

    def send_activation_email(self, request: Request, user: User) -> bool:
        mail_subject = "Activate your user account"
        message = render_to_string(
            "template_activate_account.html",
            {
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_token_generator.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            },
        )
        to_email = user.email

        return self.send_email(mail_subject, message, to_email)

    def send_reset_password_email(self, request: Request, user: User) -> bool:
        mail_subject = "Password Reset request"
        message = render_to_string(
            "template_reset_password.html",
            {
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_token_generator.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            },
        )
        to_email = user.email

        return self.send_email(mail_subject, message, to_email)
