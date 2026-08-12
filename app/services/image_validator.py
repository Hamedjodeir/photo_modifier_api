from io import BytesIO

from PIL import Image


class ImageValidator:


    def validate(
        self,
        image_bytes: bytes
    ) -> Image.Image:

        try:

            image = Image.open(
                BytesIO(image_bytes)
            )

            image.verify()

            return image


        except Exception as exc:

            raise ValueError(
                "Invalid image file"
            ) from exc