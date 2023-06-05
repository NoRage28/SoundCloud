from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from typing import Optional
from drf_spectacular.extensions import OpenApiAuthenticationExtension

User = get_user_model()


class CustomBackendAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request) -> Optional[tuple]:
        authorization_header = authentication.get_authorization_header(request).split()

        if not authorization_header or authorization_header[0].lower() != b"token":
            return None

        if len(authorization_header) == 1:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. Credentials didn't provided"
            )
        elif len(authorization_header) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. Token string shouldn't contain spaces"
            )

        try:
            access_token = authorization_header[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                "Access token has expired. Please login again"
            )
        except jwt.PyJWTError:
            raise exceptions.AuthenticationFailed(
                "Invalid authentication. Couldn't decode token"
            )

        user = User.objects.filter(id=payload["user_id"]).first()
        if user is None:
            raise exceptions.AuthenticationFailed("User not found")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")

        return user, None


class CustomAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "users.services.auth_backend.CustomBackendAuthentication"
    name = "CustomBackendAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Token <token_value>",
        }
