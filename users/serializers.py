from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

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
        return attrs
