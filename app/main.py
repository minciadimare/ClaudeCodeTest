from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import health

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


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Armochromia Classifier API"}
