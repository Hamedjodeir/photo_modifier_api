import os


MAX_UPLOAD_SIZE = int(
    os.getenv(
        "MAX_UPLOAD_SIZE",
        25 * 1024 * 1024,
    )
)


MAX_IMAGE_PIXELS = int(
    os.getenv(
        "MAX_IMAGE_PIXELS",
        100_000_000,
    )
)


MAX_ANIMATION_FRAMES = int(
    os.getenv(
        "MAX_ANIMATION_FRAMES",
        500,
    )
)


ALLOWED_INPUT_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
    "GIF",
    "BMP",
    "TIFF",
    "AVIF",
}


SUPPORTED_OUTPUT_FORMATS = {
    "jpeg",
    "jpg",
    "png",
    "webp",
    "avif",
    "gif",
    "bmp",
    "tiff",
}