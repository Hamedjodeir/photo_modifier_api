from typing import Literal

from pydantic import BaseModel, Field


OutputFormat = Literal[
    "jpeg",
    "jpg",
    "png",
    "webp",
    "avif",
    "gif",
    "bmp",
    "tiff",
]


ResizeFit = Literal[
    "contain",
    "cover",
    "stretch",
]


AnimationMode = Literal[
    "preserve",
    "first_frame",
    "reject",
]


class ResizeOptions(BaseModel):

    width: int | None = Field(
        default=None,
        gt=0,
        le=20_000,
    )

    height: int | None = Field(
        default=None,
        gt=0,
        le=20_000,
    )

    fit: ResizeFit = "contain"

    def has_resize(self) -> bool:
        return (
            self.width is not None
            or self.height is not None
        )


class CropOptions(BaseModel):

    x: int = Field(
        default=0,
        ge=0,
    )

    y: int = Field(
        default=0,
        ge=0,
    )

    width: int = Field(
        gt=0,
        le=20_000,
    )

    height: int = Field(
        gt=0,
        le=20_000,
    )


class RotationOptions(BaseModel):

    degrees: Literal[
        0,
        90,
        180,
        270,
    ] = 0

    auto_orient: bool = True

    flip_horizontal: bool = False

    flip_vertical: bool = False


class MetadataOptions(BaseModel):

    preserve: bool = False

    dpi: int | None = Field(
        default=None,
        gt=0,
        le=2400,
    )


class OutputOptions(BaseModel):

    format: OutputFormat

    quality: int = Field(
        default=85,
        ge=1,
        le=100,
    )

    lossless: bool = False

    progressive: bool = True

    compression_level: int = Field(
        default=6,
        ge=0,
        le=9,
    )

    method: int = Field(
        default=6,
        ge=0,
        le=6,
    )


class BackgroundOptions(BaseModel):

    color: str = Field(
        default="#FFFFFF",
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )


class ImageProcessingOptions(BaseModel):

    output: OutputOptions

    resize: ResizeOptions | None = None

    crop: CropOptions | None = None

    rotation: RotationOptions = RotationOptions()

    metadata: MetadataOptions = MetadataOptions()

    background: BackgroundOptions = BackgroundOptions()

    animation: AnimationMode = "preserve"