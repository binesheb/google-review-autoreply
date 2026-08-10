from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db import Base, engine
from app import models  # noqa: F401 - registers ORM models
from app.api.reviews import router as reviews_router
from app.api.settings import router as settings_router
from app.api.health import router as health_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Jayalakshmi Review Intelligence Platform", version="0.1.0")
app.include_router(reviews_router)
app.include_router(settings_router)
app.include_router(health_router)

frontend = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=frontend), name="static")

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(frontend / "index.html")
