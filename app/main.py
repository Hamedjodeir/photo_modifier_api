from fastapi import FastAPI


app = FastAPI(
    title="Photo Modifier API",
    description="Image processing and conversion API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }