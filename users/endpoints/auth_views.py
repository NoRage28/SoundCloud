from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from users.services import spotify
from django.conf import settings

from users.serializers.auth_serializers import (
    SignUpSerializer,
    SignInSerializer,
    RefreshAccessTokenSerializer,
    ChangePasswordSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer,
)
from users.utils import EmailSender
from users.tokens import (
    account_token_generator,
    generate_access_token,
    generate_refresh_token,
)

User = get_user_model()


class SpotifyLoginAPIView(views.APIView):
    def get(self, request):
        return render(
            request,
            "oauth/login_spotify.html",
            {"spotify_client_id": settings.SPOTIFY_CLIENT_ID},
        )


class SpotifyAuthAPIView(views.APIView):
    def get(self, request):
        user = spotify.spotify_auth(request.query_params.get("code"))
        if user:
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            data = {
                "user_id": user.id,
                "user_email": user.email,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Something went wrong. Please try again"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserSignUpAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_email = EmailSender().send_activation_email(request=request, user=user)
        if send_email:
            return Response(
                {"user_data": serializer.data, "send_email": True},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"user_data": serializer.data, "send_email": False},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ActivateAccountAPIView(views.APIView):
    @extend_schema(
        description="Activate user account",
        responses={
            status.HTTP_200_OK: {"success": True},
            status.HTTP_400_BAD_REQUEST: {"success": False},
        },
        parameters=[
            OpenApiParameter(
                name="uidb64",
                description="Base64 encoded user ID",
                required=True,
                type=str,
                location="path",
            ),
            OpenApiParameter(
                name="token",
                description="Account activation token",
                required=True,
                type=str,
                location="path",
            ),
        ],
    )
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


class SignInAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignInSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        data = {
            "user_id": user.id,
            "user_email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        return Response(data=data, status=status.HTTP_200_OK)


class RefreshAccessTokenAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshAccessTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = generate_access_token(serializer.validated_data.get("user"))
        return Response({"access_token": access_token}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class ResetPasswordRequestAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_email = EmailSender().send_reset_password_email(
            request=request, user=serializer.validated_data.get("user")
        )
        if send_email:
            return Response(
                {"email": serializer.data, "send_email": True},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"email": serializer.data, "send_email": False},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResetPasswordConfirmAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordConfirmSerializer

    def update(self, request, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(kwargs["uidb64"]))
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user and account_token_generator.check_token(user, kwargs["token"]):
            instance = user
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)
