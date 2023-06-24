from core.settings import USER_IMAGE_SIZE_MB_LIMIT
from django.core.exceptions import ValidationError
import os


def get_path_upload_avatar(instance, file: str) -> str:
    return os.path.join("media", "avatars", str(instance.pk), file)


def get_path_upload_album_cover(instance, file: str) -> str:
    return os.path.join("media", "albums", str(instance.user.pk), file)


def get_path_upload_track(instance, file: str) -> str:
    return os.path.join("media", "tracks", str(instance.user.pk), file)


def get_path_upload_playlist_cover(instance, file: str) -> str:
    return os.path.join("media", "playlists", str(instance.user.pk), file)


def get_path_upload_track_cover(instance, file: str) -> str:
    return os.path.join("media", "tracks", "covers", str(instance.user.pk), file)


def validate_size_image(file_obj):
    if file_obj.size > USER_IMAGE_SIZE_MB_LIMIT * 1024 * 1024:
        raise ValidationError(
            f"Your file shouldn't be more than {USER_IMAGE_SIZE_MB_LIMIT}MB"
        )


def delete_old_file(path_file):
    if os.path.exists(path_file):
        os.remove(path_file)
