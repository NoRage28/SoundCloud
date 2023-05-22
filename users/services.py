from core.settings import USER_IMAGE_SIZE_MB_LIMIT
from django.core.exceptions import ValidationError

def get_path_upload_user_image(instance, file):
    return f"user_image/{instance.id}/{file}"

def validate_size_image(file_obj):
    if file_obj > USER_IMAGE_SIZE_MB_LIMIT * 1024 * 1024:
        raise ValidationError(f"Your file shouldn't be more than {USER_IMAGE_SIZE_MB_LIMIT}MB")

