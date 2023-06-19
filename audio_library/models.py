from django.db import models
from users.models import User
from django.core.validators import FileExtensionValidator
from core.services import (
    validate_size_image,
    get_path_upload_album_cover,
    get_path_upload_track,
    get_path_upload_playlist_cover,
)


class License(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="licenses")
    text = models.TextField(max_length=1500)


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500)
    private = models.BooleanField(default=False)
    cover = models.ImageField(
        upload_to=get_path_upload_album_cover,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg"]),
            validate_size_image,
        ],
    )


class Track(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=150)
    license = models.ForeignKey(
        License, on_delete=models.PROTECT, related_name="tracks_license"
    )
    genre = models.ManyToManyField(Genre, related_name="tracks_genre")
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, blank=True, null=True)
    authors_link = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    auditions = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    user_like = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="liked_tracks"
    )
    file = models.FileField(
        upload_to=get_path_upload_track,
        validators=[FileExtensionValidator(allowed_extensions=["mp3", "wav"])],
    )

    def __str__(self):
        return f"{self.user} - {self.title}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    track = models.ForeignKey(
        Track, on_delete=models.CASCADE, related_name="track_comments"
    )
    text = models.TextField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)


class PlayList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    title = models.CharField(max_length=100)
    track = models.ManyToManyField(Track, related_name="track_playlist")
    cover = models.ImageField(
        upload_to=get_path_upload_playlist_cover,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg"]),
            validate_size_image,
        ],
    )
