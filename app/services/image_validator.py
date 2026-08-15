from __future__ import annotations

from io import BytesIO
import warnings

from PIL import (
    Image,
    UnidentifiedImageError,
)

from app.core.config import (
    ALLOWED_INPUT_FORMATS,
    MAX_ANIMATION_FRAMES,
    MAX_IMAGE_PIXELS,
    MAX_UPLOAD_SIZE,
)


class ImageValidationError(Exception):
    """Raised when uploaded image data is invalid."""


class UnsupportedImageFormatError(Exception):
    """Raised when the image format is not supported."""


class ImageValidator:

    def validate_size(
        self,
        image_bytes: bytes,
    ) -> None:

        if not image_bytes:
            raise ImageValidationError(
                "The uploaded file is empty."
            )

        if len(image_bytes) > MAX_UPLOAD_SIZE:
            raise ImageValidationError(
                "The uploaded file exceeds the maximum "
                f"allowed size of "
                f"{MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
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

            raise ImageValidationError(
                "The image dimensions are too large."
            ) from exc

        except Image.DecompressionBombWarning as exc:

            raise ImageValidationError(
                "The image dimensions are too large."
            ) from exc

        except (
            UnidentifiedImageError,
            OSError,
            SyntaxError,
        ) as exc:

            raise ImageValidationError(
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

            raise ImageValidationError(
                "The uploaded file could not be decoded."
            ) from exc

        actual_format = image.format

        if actual_format not in ALLOWED_INPUT_FORMATS:

            raise UnsupportedImageFormatError(
                f"Input image format '{actual_format}' "
                "is not supported."
            )

        width, height = image.size

        total_pixels = width * height

        if total_pixels > MAX_IMAGE_PIXELS:

            raise ImageValidationError(
                "The image contains too many pixels."
            )

        frame_count = getattr(
            image,
            "n_frames",
            1,
        )

        if frame_count > MAX_ANIMATION_FRAMES:

            raise ImageValidationError(
                "The animated image contains too many frames."
            )

        return image