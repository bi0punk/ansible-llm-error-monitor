"""Application entrypoint – exposes `app` for uvicorn."""
from app.routes import app  # noqa: F401  re-export

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
