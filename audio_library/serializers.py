from rest_framework import serializers
from audio_library import models
from core.services import delete_old_file


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ("id", "name")


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.License
        fields = ("id", "text")

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Album
        fields = ("id", "name", "description", "cover", "private")

    def update(self, instance, validated_data):
        delete_old_file(instance.cover.path)
        return super().update(instance, validated_data)
