from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
)

from fastapi.responses import Response

from app.services.image_converter import ImageConverter
from app.services.image_validator import ImageValidator


router = APIRouter(
    prefix="/v1",
    tags=["Image Conversion"]
)


converter = ImageConverter()
validator = ImageValidator()



@router.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    format: str = Form(...),
    quality: int = Form(85),
):

    try:

        image_bytes = await file.read()


        validator.validate(
            image_bytes
        )


        converted = converter.convert(
            image_bytes,
            format,
            quality
        )


        media_type = (
            f"image/{format.lower()}"
        )


        return Response(
            content=converted,
            media_type=media_type,
            headers={
                "Content-Disposition":
                f"attachment; filename=converted.{format}"
            }
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )