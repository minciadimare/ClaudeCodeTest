from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import init_db
from app.routers import health, inference, admin, pages
from app.config import settings

app = FastAPI(
    title="Armochromia Classifier",
    description="Image-based personal color season classification system",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(inference.router)
app.include_router(admin.router)
app.include_router(pages.router)

# Serve media files
storage_path = Path(settings.storage_path)
media_path = storage_path / "images"
if not media_path.exists():
    media_path.mkdir(parents=True, exist_ok=True)

app.mount("/media", StaticFiles(directory=str(media_path)), name="media")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Armochromia Classifier API", "docs_url": "/docs"}
