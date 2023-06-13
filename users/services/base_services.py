from core.settings import USER_IMAGE_SIZE_MB_LIMIT
from django.core.exceptions import ValidationError
import os


def get_path_upload_avatar(instance, file: str) -> str:
    return os.path.join("media", "avatars", str(instance.pk), file)


def validate_size_image(file_obj):
    if file_obj.size > USER_IMAGE_SIZE_MB_LIMIT * 1024 * 1024:
        raise ValidationError(
            f"Your file shouldn't be more than {USER_IMAGE_SIZE_MB_LIMIT}MB"
        )
