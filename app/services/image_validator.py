from __future__ import annotations

from io import BytesIO
import warnings

from PIL import (
    Image,
    UnidentifiedImageError,
)
from app.core.errors import (
    InvalidImageError,
    UnsupportedFormatError,
)
from app.core.config import settings


ALLOWED_INPUT_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
    "GIF",
    "BMP",
    "TIFF",
    "AVIF",
}


class ImageValidator:

    def validate_size(
        self,
        image_bytes: bytes,
    ) -> None:

        if not image_bytes:
            raise InvalidImageError(
                "The uploaded file is empty."
            )

        if len(image_bytes) > settings.max_upload_size:
            raise InvalidImageError(
                "The uploaded file exceeds the maximum "
                f"allowed size of "
                f"{settings.max_upload_size // (1024 * 1024)} MB."
            )

    def open_and_validate(
        self,
        image_bytes: bytes,
    ) -> Image.Image:

        self.validate_size(
            image_bytes
        )

        try:

            with warnings.catch_warnings():

                warnings.simplefilter(
                    "error",
                    Image.DecompressionBombWarning,
                )

                image = Image.open(
                    BytesIO(image_bytes)
                )

                image.verify()

        except Image.DecompressionBombError as exc:

            raise InvalidImageError(
                "The image dimensions are too large."
            ) from exc

        except Image.DecompressionBombWarning as exc:

            raise InvalidImageError(
                "The image dimensions are too large."
            ) from exc

        except (
            UnidentifiedImageError,
            OSError,
            SyntaxError,
        ) as exc:

            raise InvalidImageError(
                "The uploaded file is not a valid image."
            ) from exc

        try:

            image = Image.open(
                BytesIO(image_bytes)
            )

        except (
            UnidentifiedImageError,
            OSError,
        ) as exc:

            raise InvalidImageError(
                "The uploaded file could not be decoded."
            ) from exc

        actual_format = image.format

        if actual_format not in ALLOWED_INPUT_FORMATS:

            raise UnsupportedFormatError(
                f"Input image format '{actual_format}' "
                "is not supported."
            )

        width, height = image.size

        total_pixels = width * height

        if total_pixels > settings.max_image_pixels:

            raise InvalidImageError(
                "The image contains too many pixels."
            )

        frame_count = getattr(
            image,
            "n_frames",
            1,
        )

        if frame_count > settings.max_animation_frames:

            raise InvalidImageError(
                "The animated image contains too many frames."
            )

        return image