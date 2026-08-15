from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def create_test_image(
    image_format: str = "JPEG",
    size: tuple[int, int] = (400, 300),
) -> bytes:
    image = Image.new(
        "RGB",
        size,
        (255, 0, 0),
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format=image_format,
    )

    return buffer.getvalue()


def create_transparent_png() -> bytes:
    image = Image.new(
        "RGBA",
        (400, 300),
        (255, 0, 0, 0),
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()

def create_animated_gif() -> bytes:
    frames = [
        Image.new(
            "RGB",
            (100, 100),
            (255, 0, 0),
        ),
        Image.new(
            "RGB",
            (100, 100),
            (0, 255, 0),
        ),
        Image.new(
            "RGB",
            (100, 100),
            (0, 0, 255),
        ),
    ]

    buffer = BytesIO()

    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=[100, 200, 300],
        loop=0,
    )

    return buffer.getvalue()

def convert(
    image_bytes: bytes,
    source_filename: str,
    output_format: str,
    **options,
):
    return client.post(
        "/v1/convert",
        files={
            "file": (
                source_filename,
                image_bytes,
                "application/octet-stream",
            )
        },
        data={
            "format": output_format,
            **{
                key: str(value)
                for key, value in options.items()
            },
        },
    )


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "status": "ok",
        "service": "Photo Modifier API",
        "version": "0.1.0",
    }


# ---------------------------------------------------------
# Basic format conversion
# ---------------------------------------------------------


def test_jpeg_to_jpeg():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "jpeg",
        quality=90,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "JPEG"
    assert output.size == (400, 300)


def test_jpeg_to_png():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "png",
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "PNG"
    assert output.size == (400, 300)


def test_jpeg_to_webp():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        quality=85,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/webp"

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "WEBP"
    assert output.size == (400, 300)


def test_png_to_jpeg():

    response = convert(
        create_test_image("PNG"),
        "test.png",
        "jpeg",
        quality=90,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "JPEG"


def test_png_to_png():

    response = convert(
        create_test_image("PNG"),
        "test.png",
        "png",
        compression_level=9,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "PNG"


def test_png_to_webp():

    response = convert(
        create_test_image("PNG"),
        "test.png",
        "webp",
        quality=85,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "WEBP"


def test_webp_to_jpeg():

    response = convert(
        create_test_image("WEBP"),
        "test.webp",
        "jpeg",
        quality=90,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "JPEG"


def test_webp_to_png():

    response = convert(
        create_test_image("WEBP"),
        "test.webp",
        "png",
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "PNG"


def test_webp_to_webp():

    response = convert(
        create_test_image("WEBP"),
        "test.webp",
        "webp",
        quality=80,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "WEBP"


def test_gif_to_webp():

    response = convert(
        create_test_image("GIF"),
        "test.gif",
        "webp",
        quality=85,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "WEBP"


# ---------------------------------------------------------
# Resize
# ---------------------------------------------------------


def test_resize_by_width():

    response = convert(
        create_test_image(
            "JPEG",
            size=(800, 600),
        ),
        "test.jpg",
        "webp",
        width=400,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.size == (400, 300)


def test_resize_by_height():

    response = convert(
        create_test_image(
            "JPEG",
            size=(800, 600),
        ),
        "test.jpg",
        "webp",
        height=300,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.size == (400, 300)


def test_resize_cover():

    response = convert(
        create_test_image(
            "JPEG",
            size=(800, 600),
        ),
        "test.jpg",
        "webp",
        width=400,
        height=400,
        fit="cover",
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.size == (400, 400)


# ---------------------------------------------------------
# Transformations
# ---------------------------------------------------------


def test_rotation():

    response = convert(
        create_test_image(
            "JPEG",
            size=(400, 300),
        ),
        "test.jpg",
        "webp",
        rotation=90,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.size == (300, 400)


def test_horizontal_flip():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        flip_horizontal=True,
    )

    assert response.status_code == 200


def test_vertical_flip():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        flip_vertical=True,
    )

    assert response.status_code == 200


# ---------------------------------------------------------
# Transparency
# ---------------------------------------------------------


def test_transparent_png_to_jpeg_with_background():

    response = convert(
        create_transparent_png(),
        "transparent.png",
        "jpeg",
        quality=90,
        background="#FFFFFF",
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "JPEG"
    assert output.mode == "RGB"


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------


def test_invalid_image():

    response = convert(
        b"this is not an image",
        "fake.jpg",
        "webp",
    )

    assert response.status_code == 400


def test_invalid_output_format():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "banana",
    )

    assert response.status_code == 422


def test_invalid_quality():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        quality=101,
    )

    assert response.status_code == 422


def test_invalid_background():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        background="not-a-color",
    )

    assert response.status_code == 422


def test_invalid_dpi():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        dpi=0,
    )

    assert response.status_code == 422


def test_partial_crop():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "webp",
        crop_x=10,
    )

    assert response.status_code == 422

def test_animated_gif_to_webp_preserves_animation():

    response = convert(
        create_animated_gif(),
        "animated.gif",
        "webp",
        animation="preserve",
        quality=85,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "WEBP"
    assert output.is_animated is True
    assert output.n_frames == 3

def test_animated_gif_to_avif_preserves_animation():

    response = convert(
        create_animated_gif(),
        "animated.gif",
        "avif",
        animation="preserve",
        quality=70,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "AVIF"
    assert output.is_animated is True
    assert output.n_frames == 3

def test_animated_gif_first_frame_to_jpeg():

    response = convert(
        create_animated_gif(),
        "animated.gif",
        "jpeg",
        animation="first_frame",
        quality=90,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "JPEG"
    assert getattr(output, "n_frames", 1) == 1

def test_animated_image_can_be_rejected():

    response = convert(
        create_animated_gif(),
        "animated.gif",
        "webp",
        animation="reject",
    )

    assert response.status_code == 400
    

def test_animation_preserve_rejects_non_animated_output():

    response = convert(
        create_animated_gif(),
        "animated.gif",
        "jpeg",
        animation="preserve",
    )

    assert response.status_code == 400

def test_jpeg_to_avif():

    response = convert(
        create_test_image("JPEG"),
        "test.jpg",
        "avif",
        quality=70,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/avif"

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "AVIF"
    assert output.size == (400, 300)


def test_avif_to_webp():

    response = convert(
        create_test_image("AVIF"),
        "test.avif",
        "webp",
        quality=85,
    )

    assert response.status_code == 200

    output = Image.open(
        BytesIO(response.content)
    )

    assert output.format == "WEBP"


def test_health_contains_service_information():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "Photo Modifier API"
    assert data["version"] == "0.1.0"


def test_readiness():

    response = client.get(
        "/ready"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"


def test_request_id_is_returned():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None
    assert len(request_id) > 0


def test_process_time_header_is_returned():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert "X-Process-Time-Ms" in (
        response.headers
    )


def test_invalid_request_has_standard_error_shape():

    response = client.post(
        "/v1/convert",
        files={
            "file": (
                "test.jpg",
                create_test_image("JPEG"),
                "image/jpeg",
            )
        },
        data={
            "format": "banana",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert "error" in data
    assert "request_id" in data

    assert data["error"]["code"] == (
        "validation_error"
    )

    assert "message" in data["error"]


def test_invalid_image_has_standard_error_shape():

    response = client.post(
        "/v1/convert",
        files={
            "file": (
                "fake.jpg",
                b"not an image",
                "image/jpeg",
            )
        },
        data={
            "format": "webp",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert "error" in data
    assert "request_id" in data

    assert data["error"]["code"] == (
        "invalid_request"
    )


def test_request_ids_are_unique():

    first = client.get(
        "/health"
    )

    second = client.get(
        "/health"
    )

    first_id = first.headers["X-Request-ID"]
    second_id = second.headers["X-Request-ID"]

    assert first_id != second_id