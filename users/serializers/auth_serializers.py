from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.conf import settings

import jwt

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"id": {"read_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=30, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ["email", "password"]

    def validate(self, attrs):
        user = User.objects.filter(email=attrs["email"]).first()
        if user is None:
            raise AuthenticationFailed("User with such email doesn't exist")
        if not user.check_password(attrs.get("password")):
            raise AuthenticationFailed("You passed a wrong password")
        attrs["user"] = user
        return attrs


class RefreshAccessTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        max_length=255, required=True, write_only=True
    )

    class Meta:
        fields = ["user_id", "refresh_token"]
        extra_kwargs = {"user_id": {"read_only": True}}

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired refresh token, please login again")
        user = User.objects.filter(id=payload.get("user_id")).first()
        if user is None:
            raise AuthenticationFailed("User not found")
        if not user.is_active:
            raise AuthenticationFailed("User is inactive")
        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password", "new_password_2"]

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_2"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match"}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password isn't correct")

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=30)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        user = User.objects.filter(email=attrs.get("email")).first()
        if user is None:
            raise serializers.ValidationError("User with such email doesn't exist")
        attrs["user"] = user
        return attrs


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )

    class Meta:
        fields = ["new_password"]

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance
