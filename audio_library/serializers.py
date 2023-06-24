from rest_framework import serializers
from audio_library import models
from core.services import delete_old_file
from users.serializers.base_serializers import AuthorSerializer


class BaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)


class GenreSerializer(BaseSerializer):
    class Meta:
        model = models.Genre
        fields = ("id", "name")


class LicenseSerializer(BaseSerializer):
    class Meta:
        model = models.License
        fields = ("id", "text")


class AlbumSerializer(BaseSerializer):
    class Meta:
        model = models.Album
        fields = ("id", "name", "description", "cover", "private")

    def update(self, instance, validated_data):
        delete_old_file(instance.cover.path)
        return super().update(instance, validated_data)


class CreateTrackSerializer(BaseSerializer):
    class Meta:
        model = models.Track
        fields = (
            "id",
            "user",
            "title",
            "license",
            "genre",
            "album",
            "authors_link",
            "private",
            "created_at",
            "auditions",
            "downloads",
            "cover",
            "file",
        )
        read_only_fields = ["auditions", "downloads", "user"]

    def update(self, instance, validated_data):
        delete_old_file(instance.file.path)
        delete_old_file(instance.cover.path)
        return super().update(instance, validated_data)


class TrackSerializer(CreateTrackSerializer):
    license = LicenseSerializer()
    genre = GenreSerializer(many=True)
    album = AlbumSerializer()
    user = AuthorSerializer()


class CreatePlayListSerializer(BaseSerializer):
    class Meta:
        model = models.PlayList
        fields = ("id", "title", "cover", "track")

    def update(self, instance, validated_data):
        delete_old_file(instance.cover.path)
        return super().update(instance, validated_data)


class PlayListSerializer(CreatePlayListSerializer):
    track = TrackSerializer(many=True, read_only=True)


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ("id", "text", "track")


class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer()

    class Meta:
        model = models.Comment
        fields = ("id", "user", "text", "track", "created_at")
