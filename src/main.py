from src.modules.test import model
from fastapi import FastAPI
from src.database.db import engine
from src.modules.test.model import Base
from src.modules.test.controller import router as test_router
from fastapi.middleware.cors import CORSMiddleware
from src.modules.post.controller import router as post_router
from src.modules.image.controller import router as image_router
from src.modules.user.controller import router as user_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path

Base.metadata.create_all(bind=engine)


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Welcome to O-Kard API 🚀"}

app.include_router(test_router, prefix="/api")
app.include_router(post_router, prefix="/api")
app.include_router(user_router, prefix="/api")
# app.include_router(image_router, prefix="/api")

