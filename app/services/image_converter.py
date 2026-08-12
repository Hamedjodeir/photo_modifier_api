from io import BytesIO

from PIL import Image


SUPPORTED_FORMATS = {
    "jpeg": "JPEG",
    "jpg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "gif": "GIF",
    "bmp": "BMP",
}


class ImageConverter:

    def convert(
        self,
        image_bytes: bytes,
        output_format: str,
        quality: int = 85,
    ) -> bytes:

        output_format = output_format.lower()

        if output_format not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}"
            )

        image = Image.open(
            BytesIO(image_bytes)
        )

        # Handle transparency problems
        if (
            output_format in ["jpeg", "jpg"]
            and image.mode in ("RGBA", "LA")
        ):
            background = Image.new(
                "RGB",
                image.size,
                (255, 255, 255)
            )

            background.paste(
                image,
                mask=image.split()[-1]
            )

            image = background


        output = BytesIO()


        save_options = {}

        if output_format in ["jpeg", "jpg", "webp"]:
            save_options["quality"] = quality


        image.save(
            output,
            format=SUPPORTED_FORMATS[output_format],
            **save_options
        )


        return output.getvalue()