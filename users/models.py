from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import FileExtensionValidator
from users.services.base_services import get_path_upload_avatar, validate_size_image


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be provided.")
        if not password:
            raise ValueError("Password must be provided.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Main User Model
    """

    email = models.EmailField(max_length=150, unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    about = models.TextField(max_length=2000, blank=True, null=True)
    avatar = models.ImageField(
        upload_to=get_path_upload_avatar,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg"]),
            validate_size_image,
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )

    def __str__(self):
        return f"{self.subscriber} subscribed to {self.user}"


class SocialLink(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_links"
    )
    link = models.URLField(max_length=255)

    def __str__(self):
        return f"{self.user} is owner for {self.link}"
