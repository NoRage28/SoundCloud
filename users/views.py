from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework import (generics, permissions, views, status)
from rest_framework.response import Response

from users.serializers import SignUpSerializer
from users.utils import EmailSender
from users.tokens import account_token_generator

User = get_user_model()


class UserSignUpView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_email = EmailSender().send_activation_email(request=request, data=serializer.data)
        if send_email:
            return Response({"user_data": serializer.data, "send_email": True}, status=status.HTTP_201_CREATED)
        return Response({"user_data": serializer.data, "send_email": False}, status=status.HTTP_400_BAD_REQUEST)


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
