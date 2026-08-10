from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db import Base, engine
from app import models  # noqa: F401
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.reviews import router as reviews_router
from app.api.settings import router as settings_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.instructions import router as instructions_router
from app.api.cases import router as cases_router
from app.api.google import router as google_router
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(reviews_router)
app.include_router(settings_router)
app.include_router(health_router)
app.include_router(knowledge_router)
app.include_router(instructions_router)
app.include_router(cases_router)
app.include_router(google_router)

frontend = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=frontend), name="static")


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(frontend / "index.html")
