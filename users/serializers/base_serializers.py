from rest_framework import serializers
from users.models import User, SocialLink


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("avatar", "username", "country", "city", "about")


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ("id", "link")


class AuthorSerializer(serializers.ModelSerializer):
    social_links = SocialLinkSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "avatar",
            "username",
            "country",
            "city",
            "about",
            "social_links",
        )
