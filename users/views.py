import jwt
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.conf import settings
from rest_framework import generics, permissions, views, status, exceptions
from rest_framework.response import Response

from users.serializers import SignUpSerializer, SignInSerializer
from users.utils import EmailSender
from users.tokens import account_token_generator, generate_access_token, generate_refresh_token

User = get_user_model()


class UserSignUpView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_email = EmailSender().send_activation_email(
            request=request, data=serializer.data
        )
        if send_email:
            return Response(
                {"user_data": serializer.data, "send_email": True},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"user_data": serializer.data, "send_email": False},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ActivateAccountView(views.APIView):
    def get(self, request, uidb64: str, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user and account_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)


class SignInView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignInSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.filter(email=serializer.data.get("email")).first()
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            data = {"user_id": user.id,
                    "user_email": user.email,
                    "access_token": access_token,
                    "refresh_token": refresh_token}
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainRefreshTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token is None:
            raise exceptions.AuthenticationFailed("Authentication credentials were not provided")
        try:
            payload = jwt.decode(refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Expired refresh token, please login again")

        user = User.objects.filter(id=payload.get("user_id")).first()
        if user is None:
            raise exceptions.AuthenticationFailed("User not found")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")
        access_token = generate_access_token(user)
        return Response({"access_token": access_token}, status=status.HTTP_200_OK)
