from fastapi import FastAPI

from app.api.convert import router as convert_router


app = FastAPI(
    title="Photo Modifier API",
    description="Image processing and conversion API",
    version="0.1.0",
)


app.include_router(
    convert_router
)


@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }