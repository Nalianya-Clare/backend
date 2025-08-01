from django.core.files.uploadedfile import UploadedFile
from rest_framework import status

from util.errors.exceptionhandler import CustomInternalServerError


class BaseValidator:
    ACCEPTED_MIME_TYPES = {}
    VALIDATOR_NAME = "file"

    @classmethod
    def validate_file_size(cls, uploaded_file: UploadedFile) -> None:
        """Validate file size based on MIME type."""
        mime_type = uploaded_file.content_type

        if mime_type not in cls.ACCEPTED_MIME_TYPES:
            raise CustomInternalServerError(
                message=str("Unsupported file type"),
                code="bad_request",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        max_size_mb = cls.ACCEPTED_MIME_TYPES[mime_type]
        max_size_bytes = max_size_mb * 1024 * 1024

        if uploaded_file.size > max_size_bytes:
            raise CustomInternalServerError(
                message=str("file uploaded too large"),
                code="bad_request",
                status_code=status.HTTP_400_BAD_REQUEST
            )

class DocumentTemplateValidator(BaseValidator):
    """Validator for Word and PowerPoint documents."""
    ACCEPTED_MIME_TYPES = {
        "application/msword": 25,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": 25,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": 25,
    }
    VALIDATOR_NAME = "document template"

class MediaFileValidator(BaseValidator):
    """Validator for PDF and video files."""
    ACCEPTED_MIME_TYPES = {
        "application/pdf": 25,
        "video/mp4": 1024,
        "video/mpeg": 1024,
        "video/quicktime": 1024,
        "audio/mpeg": 1024,
        "audio/wav": 1024,
        "audio/x-wav": 1024,
        "audio/vnd.wave": 1024,
        "audio/wave": 1024,
        "audio/ogg": 1024,
        "audio/mp3": 1024,
        "image/png": 10,
        "image/jpeg": 10,
    }
    VALIDATOR_NAME = "media file"

class ImageFileValidator(BaseValidator):
    """Validator for image files."""
    ACCEPTED_MIME_TYPES = {

    }
    VALIDATOR_NAME = "image file"