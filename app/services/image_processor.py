from __future__ import annotations

from io import BytesIO
from typing import Any

import pillow_avif
from PIL import Image, ImageOps

from app.schemas.image import ImageProcessingOptions


FORMAT_MAP = {
    "jpeg": "JPEG",
    "jpg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "avif": "AVIF",
    "gif": "GIF",
    "bmp": "BMP",
    "tiff": "TIFF",
}

ANIMATED_OUTPUT_FORMATS = {
    "gif",
    "webp",
    "avif",
}

MIME_TYPES = {
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "avif": "image/avif",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
}


class ImageProcessingError(Exception):
    """Raised when an image cannot be processed."""


class ImageProcessor:
    def _prepare_frame(
        self,
        image: Image.Image,
        options: ImageProcessingOptions,
    ) -> Image.Image:

        image = self._prepare_image(
            image,
            options,
        )

        image = self._apply_crop(
            image,
            options,
        )

        image = self._apply_resize(
            image,
            options,
        )

        output_format = (
            options.output.format.lower()
        )

        image = self._prepare_output_mode(
            image,
            output_format,
            options,
        )

        return image

        
    def _extract_metadata(
        self,
        image: Image.Image,
    ) -> dict[str, object]:

        metadata: dict[str, object] = {}

        exif = image.info.get("exif")

        if exif:
            metadata["exif"] = exif

        icc_profile = image.info.get("icc_profile")

        if icc_profile:
            metadata["icc_profile"] = icc_profile

        xmp = image.info.get("xmp")

        if xmp:
            metadata["xmp"] = xmp

        dpi = image.info.get("dpi")

        if dpi:
            metadata["dpi"] = dpi

        return metadata

    def _extract_animation_data(
        self,
        image: Image.Image,
    ) -> tuple[list[Image.Image], list[int], int]:
        """
        Extract all frames, frame durations, and loop count
        from a multiframe image.
        """

        frame_count = getattr(
            image,
            "n_frames",
            1,
        )

        frames: list[Image.Image] = []
        durations: list[int] = []

        loop = int(
            image.info.get(
                "loop",
                0,
            )
        )

        current_position = image.tell()

        try:
            for frame_index in range(frame_count):

                image.seek(frame_index)

                frame = image.convert("RGBA").copy()

                frames.append(frame)

                duration = image.info.get(
                    "duration",
                    100,
                )

                if isinstance(duration, (list, tuple)):
                    duration = duration[frame_index]

                durations.append(
                    int(duration or 100)
                )

        finally:
            image.seek(current_position)

        return frames, durations, loop

    def process(
        self,
        image_bytes: bytes,
        options: ImageProcessingOptions,
    ) -> tuple[bytes, str]:

        try:
            image = Image.open(
                BytesIO(image_bytes)
            )

            image.load()

        except Exception as exc:
            raise ImageProcessingError(
                "The uploaded file is not a valid image."
            ) from exc

        metadata = self._extract_metadata(
            image
        )

        output_format = options.output.format.lower()

        if output_format not in FORMAT_MAP:
            raise ImageProcessingError(
                f"Unsupported output format: {output_format}"
            )

        self._validate_animation(
            image,
            options,
        )

        is_animated = getattr(
            image,
            "is_animated",
            False,
        )

        if (
            is_animated
            and options.animation == "preserve"
        ):

            frames, durations, loop = (
                self._extract_animation_data(
                    image
                )
            )

            processed_frames = []

            for frame in frames:

                frame = self._prepare_frame(
                    frame,
                    options,
                )

                processed_frames.append(
                    frame
                )

            output = self._encode(
                processed_frames[0],
                output_format,
                options,
                metadata,
                append_images=processed_frames[1:],
                durations=durations,
                loop=loop,
                save_all=True,
            )

        else:

            if (
                is_animated
                and options.animation == "first_frame"
            ):

                image.seek(0)

            image = self._prepare_frame(
                image,
                options,
            )

            output = self._encode(
                image,
                output_format,
                options,
                metadata,
            )

        return output, MIME_TYPES[output_format]

    # ---------------------------------------------------------
    # Animation
    # ---------------------------------------------------------

    def _validate_animation(
        self,
        image: Image.Image,
        options: ImageProcessingOptions,
    ) -> None:

        is_animated = getattr(
            image,
            "is_animated",
            False,
        )

        if not is_animated:
            return

        if options.animation == "reject":

            raise ImageProcessingError(
                "Animated images are not allowed for this request."
            )

        output_format = (
            options.output.format.lower()
        )

        if (
            options.animation == "preserve"
            and output_format
            not in ANIMATED_OUTPUT_FORMATS
        ):

            raise ImageProcessingError(
                "The requested output format does not "
                "support animation. Use animation="
                "'first_frame' or choose GIF, WebP, or AVIF."
            )

    # ---------------------------------------------------------
    # Orientation / rotation / flipping
    # ---------------------------------------------------------

    def _prepare_image(
        self,
        image: Image.Image,
        options: ImageProcessingOptions,
    ) -> Image.Image:

        rotation = options.rotation

        if rotation.auto_orient:

            image = ImageOps.exif_transpose(
                image
            )

        if rotation.degrees:

            image = image.rotate(
                rotation.degrees,
                expand=True,
            )

        if rotation.flip_horizontal:

            image = ImageOps.mirror(
                image
            )

        if rotation.flip_vertical:

            image = ImageOps.flip(
                image
            )

        return image

    # ---------------------------------------------------------
    # Crop
    # ---------------------------------------------------------

    def _apply_crop(
        self,
        image: Image.Image,
        options: ImageProcessingOptions,
    ) -> Image.Image:

        crop = options.crop

        if crop is None:
            return image

        right = crop.x + crop.width
        bottom = crop.y + crop.height

        if right > image.width or bottom > image.height:

            raise ImageProcessingError(
                "Crop dimensions exceed the image dimensions."
            )

        return image.crop(
            (
                crop.x,
                crop.y,
                right,
                bottom,
            )
        )

    # ---------------------------------------------------------
    # Resize
    # ---------------------------------------------------------

    def _apply_resize(
        self,
        image: Image.Image,
        options: ImageProcessingOptions,
    ) -> Image.Image:

        resize = options.resize

        if resize is None or not resize.has_resize():
            return image

        width = resize.width
        height = resize.height

        if width is None:

            ratio = height / image.height

            width = max(
                1,
                round(image.width * ratio),
            )

        elif height is None:

            ratio = width / image.width

            height = max(
                1,
                round(image.height * ratio),
            )

        if resize.fit == "stretch":

            return image.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

        if resize.fit == "contain":

            return ImageOps.contain(
                image,
                (width, height),
                method=Image.Resampling.LANCZOS,
            )

        if resize.fit == "cover":

            return ImageOps.fit(
                image,
                (width, height),
                method=Image.Resampling.LANCZOS,
            )

        raise ImageProcessingError(
            f"Unsupported resize mode: {resize.fit}"
        )

    # ---------------------------------------------------------
    # Output preparation
    # ---------------------------------------------------------

    def _prepare_output_mode(
        self,
        image: Image.Image,
        output_format: str,
        options: ImageProcessingOptions,
    ) -> Image.Image:

        requires_rgb = output_format in {
            "jpeg",
            "jpg",
        }

        if requires_rgb and image.mode in {
            "RGBA",
            "LA",
            "P",
        }:

            background = self._create_background(
                image,
                options.background.color,
            )

            if image.mode == "P":
                image = image.convert("RGBA")

            background.paste(
                image,
                mask=image.getchannel("A")
                if "A" in image.getbands()
                else None,
            )

            return background

        if output_format in {
            "jpeg",
            "jpg",
            "bmp",
        }:

            return image.convert("RGB")

        return image

    # ---------------------------------------------------------
    # Encoding
    # ---------------------------------------------------------

    def _encode(
        self,
        image: Image.Image,
        output_format: str,
        options: ImageProcessingOptions,
        metadata: dict[str, object],
        append_images: list[Image.Image] | None = None,
        durations: list[int] | None = None,
        loop: int = 0,
        save_all: bool = False,
    ) -> bytes:

        output = BytesIO()

        save_options: dict[str, Any] = {}

        output_options = options.output
        if append_images:
            save_options["append_images"] = append_images

        if save_all:
            save_options["save_all"] = True

        if durations:
            save_options["duration"] = durations

        if save_all:
            save_options["loop"] = loop
        if options.metadata.preserve:

            for key in (
                "exif",
                "icc_profile",
                "xmp",
            ):

                value = metadata.get(key)

                if value is not None:
                    save_options[key] = value
        if output_format in {
            "jpeg",
            "jpg",
        }:

            save_options.update(
                {
                    "quality": output_options.quality,
                    "optimize": True,
                    "progressive": output_options.progressive,
                }
            )

        elif output_format == "png":

            save_options.update(
                {
                    "compress_level":
                        output_options.compression_level,
                    "optimize": False,
                }
            )

        elif output_format == "webp":

            save_options.update(
                {
                    "quality": output_options.quality,
                    "lossless": output_options.lossless,
                    "method": output_options.method,
                }
            )

        elif output_format == "avif":

            save_options.update(
                {
                    "quality": output_options.quality,
                    "lossless": output_options.lossless,
                }
            )

        elif output_format == "gif":

            save_options.update(
                {
                    "optimize": True,
                }
            )

        dpi = options.metadata.dpi

        if dpi is not None:

            save_options["dpi"] = (
                dpi,
                dpi,
            )

        elif options.metadata.preserve:

            original_dpi = metadata.get("dpi")

            if original_dpi is not None:

                save_options["dpi"] = original_dpi

                
        image.save(
            output,
            format=FORMAT_MAP[output_format],
            **save_options,
        )

        return output.getvalue()

    # ---------------------------------------------------------
    # Background
    # ---------------------------------------------------------

    def _create_background(
        self,
        image: Image.Image,
        color: str,
    ) -> Image.Image:

        try:

            background = Image.new(
                "RGB",
                image.size,
                color,
            )

        except ValueError as exc:

            raise ImageProcessingError(
                f"Invalid background color: {color}"
            ) from exc

        return background

    def _extract_metadata(
        self,
        image: Image.Image,
    ) -> dict[str, object]:

        metadata: dict[str, object] = {}

        exif = image.info.get(
            "exif"
        )

        if exif:
            metadata["exif"] = exif

        icc_profile = image.info.get(
            "icc_profile"
        )

        if icc_profile:
            metadata["icc_profile"] = icc_profile

        xmp = image.info.get(
            "xmp"
        )

        if xmp:
            metadata["xmp"] = xmp

        return metadata