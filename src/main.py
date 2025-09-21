from fastapi import FastAPI
from src.database.db import engine
from src.modules.test.model import Base
from fastapi.middleware.cors import CORSMiddleware

from src.modules.test import model as test_model
from src.modules.post import model as post_model
from src.modules.image import model as image_model
from src.modules.user import model as user_model
from src.modules.campaign import model as campaign_model
from src.modules.reward import model as reward_model
from src.modules.contributor import model as contributor_model
from src.modules.payment import model as payment_model

from src.modules.test.controller import router as test_router
from src.modules.post.controller import router as post_router
from src.modules.image.controller import router as image_router
from src.modules.user.controller import router as user_router
from src.modules.country.controller import router as country_router
from src.modules.payment.controller import router as payment_router
from src.modules.comment.controller import router as comment_router
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
app.include_router(image_router, prefix="/api")
app.include_router(country_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(comment_router, prefix="/api")
# app.include_router(image_router, prefix="/api")

