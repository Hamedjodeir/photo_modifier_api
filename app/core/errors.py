class PhotoModifierError(Exception):
    """Base exception for application-level errors."""

    status_code = 400
    code = "application_error"

    def __init__(
        self,
        message: str,
        details=None,
    ):
        super().__init__(message)

        self.message = message
        self.details = details


class InvalidImageError(PhotoModifierError):
    status_code = 400
    code = "invalid_request"


class UnsupportedFormatError(PhotoModifierError):
    status_code = 415
    code = "unsupported_media_type"


class FileTooLargeError(PhotoModifierError):
    status_code = 413
    code = "file_too_large"


class InvalidProcessingOptionsError(PhotoModifierError):
    status_code = 422
    code = "validation_error"


class ImageProcessingError(PhotoModifierError):
    status_code = 400
    code = "image_processing_error"