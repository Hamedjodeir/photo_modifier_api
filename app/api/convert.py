from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import Response
from pydantic import ValidationError

from app.core.config import MAX_UPLOAD_SIZE

from app.schemas.image import (
    BackgroundOptions,
    CropOptions,
    ImageProcessingOptions,
    MetadataOptions,
    OutputOptions,
    ResizeOptions,
    RotationOptions,
)

from app.services.image_processor import (
    ImageProcessingError,
    ImageProcessor,
)

from app.services.image_validator import (
    ImageValidationError,
    ImageValidator,
    UnsupportedImageFormatError,
)

from app.utils.uploads import (
    UploadTooLargeError,
    read_upload_limited,
)


router = APIRouter(
    prefix="/v1",
    tags=["Image Conversion"],
)


processor = ImageProcessor()

validator = ImageValidator()


@router.post("/convert")
async def convert_image(
    file: UploadFile = File(...),

    format: str = Form(...),

    quality: int = Form(85),

    lossless: bool = Form(False),

    width: int | None = Form(None),

    height: int | None = Form(None),

    fit: str = Form("contain"),

    crop_x: int | None = Form(None),

    crop_y: int | None = Form(None),

    crop_width: int | None = Form(None),

    crop_height: int | None = Form(None),

    rotation: int = Form(0),

    auto_orient: bool = Form(True),

    flip_horizontal: bool = Form(False),

    flip_vertical: bool = Form(False),

    preserve_metadata: bool = Form(False),

    dpi: int | None = Form(None),

    background: str = Form("#FFFFFF"),

    progressive: bool = Form(True),

    compression_level: int = Form(6),

    method: int = Form(6),

    animation: str = Form("preserve"),
):
    try:

        # -----------------------------------------------------
        # Read upload with a hard size limit
        # -----------------------------------------------------

        try:

            image_bytes = await read_upload_limited(
                file,
                MAX_UPLOAD_SIZE,
            )
            try:

                output_options = OutputOptions(
                    format=format.lower(),
                    quality=quality,
                    lossless=lossless,
                    progressive=progressive,
                    compression_level=compression_level,
                    method=method,
                )

            except ValidationError as exc:

                raise HTTPException(
                    status_code=422,
                    detail=exc.errors(),
                ) from exc

        except UploadTooLargeError as exc:

            raise HTTPException(
                status_code=413,
                detail=str(exc),
            ) from exc

        # -----------------------------------------------------
        # Validate actual image data
        # -----------------------------------------------------

        validator.open_and_validate(
            image_bytes
        )

        # -----------------------------------------------------
        # Build crop options
        # -----------------------------------------------------

        crop = None

        crop_values = (
            crop_x,
            crop_y,
            crop_width,
            crop_height,
        )

        if all(
            value is not None
            for value in crop_values
        ):

            crop = CropOptions(
                x=crop_x,
                y=crop_y,
                width=crop_width,
                height=crop_height,
            )

        elif any(
            value is not None
            for value in crop_values
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "crop_x, crop_y, crop_width, "
                    "and crop_height must be provided together."
                ),
            )

        # -----------------------------------------------------
        # Build resize options
        # -----------------------------------------------------

        resize = None

        if (
            width is not None
            or height is not None
        ):

            resize = ResizeOptions(
                width=width,
                height=height,
                fit=fit,
            )

        # -----------------------------------------------------
        # Build complete processing options
        # -----------------------------------------------------

        options = ImageProcessingOptions(
            output=output_options,

            resize=resize,

            crop=crop,

            rotation=RotationOptions(
                degrees=rotation,
                auto_orient=auto_orient,
                flip_horizontal=flip_horizontal,
                flip_vertical=flip_vertical,
            ),

            metadata=MetadataOptions(
                preserve=preserve_metadata,
                dpi=dpi,
            ),

            background=BackgroundOptions(
                color=background,
            ),

            animation=animation,
        )

        # -----------------------------------------------------
        # Process
        # -----------------------------------------------------

        converted, media_type = processor.process(
            image_bytes,
            options,
        )

        extension = (
            "jpg"
            if format.lower() in {"jpg", "jpeg"}
            else format.lower()
        )

        # -----------------------------------------------------
        # Return converted image
        # -----------------------------------------------------

        return Response(
            content=converted,
            media_type=media_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="converted.{extension}"'
                )
            },
        )

    except UnsupportedImageFormatError as exc:

        raise HTTPException(
            status_code=415,
            detail=str(exc),
        ) from exc

    except ImageValidationError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValidationError as exc:

        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc

    except ImageProcessingError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc