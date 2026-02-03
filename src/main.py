from fastapi import FastAPI, Request
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
from src.modules.model import model as predict_model

from src.modules.notification import model as notification_model
from src.modules.progress import model as progress_model

from src.modules.test.controller import router as test_router
from src.modules.post.controller import router as post_router
from src.modules.image.controller import router as image_router
from src.modules.user.controller import router as user_router
from src.modules.country.controller import router as country_router
from src.modules.payment.controller import router as payment_router
from src.modules.comment.controller import router as comment_router
from src.modules.model.controller import router as predict_router
from src.modules.home.controller import router as home_router
from src.modules.edit_request.controller import router as edit_request_router
from src.modules.progress.controller import router as progress_router
from src.modules.report.controller import router as report_router

from src.modules.notification.controller import router as notification_router
from src.modules.dashboard.controller import router as dashboard_router

from src.modules.search.controller import router as search_router
from src.modules.for_you.controller import router as for_you_router
from src.modules.post_recommend.controller import router as post_recommend_router
from src.modules.progress.controller import router as progress_router

from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

class StaticCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/uploads"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"

        return response

Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
# app.mount("/uploads", StaticFiles(directory=BASE_DIR / "uploads"), name="uploads")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(StaticCORSMiddleware)

app.mount("/uploads",StaticFiles(directory=BASE_DIR / "uploads"),name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to O-Kard API 🚀"}

app.include_router(test_router, prefix="/api")
app.include_router(for_you_router, prefix="/api")
app.include_router(post_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(image_router, prefix="/api")
app.include_router(country_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(comment_router, prefix="/api")
app.include_router(predict_router, prefix="/api")
app.include_router(notification_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(post_recommend_router, prefix="/api")
app.include_router(home_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(edit_request_router, prefix="/api")
app.include_router(report_router, prefix="/api")