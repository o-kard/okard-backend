from fastapi import FastAPI, Request
from src.database.db import engine
from src.modules.test.model import Base
from fastapi.middleware.cors import CORSMiddleware

from src.modules.test import model as test_model
from src.modules.campaign import model as campaign_model
from src.modules.media import model as media_model
from src.modules.user import model as user_model
from src.modules.information import model as information_model
from src.modules.reward import model as reward_model
from src.modules.contributor import model as contributor_model
from src.modules.creator import model as creator_model
from src.modules.payment import model as payment_model
from src.modules.model import model as predict_model

from src.modules.notification import model as notification_model
from src.modules.progress import model as progress_model

from src.modules.test.controller import router as test_router
from src.modules.campaign.controller import router as campaign_router
from src.modules.media.controller import router as media_router
from src.modules.user.controller import router as user_router
from src.modules.creator.controller import router as creator_router
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
from src.modules.contributor.controller import router as contributor_router

from src.modules.search.controller import router as search_router
from src.modules.for_you.controller import router as for_you_router
from src.modules.campaign_recommend.controller import router as campaign_recommend_router
from src.modules.bookmark.controller import router as bookmark_router
from src.modules.edit_request import model as edit_request_model
from src.modules.common.enums import EditRequestStatus

from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path
import os

class StaticCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/uploads"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"

        return response

import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from src.database.db import SessionLocal
from src.modules.common.enums import CampaignState

async def expire_campaigns_task():
    while True:
        try:
            db = SessionLocal()
            now_utc = datetime.now(timezone.utc)
            # Find published campaigns that have passed their end date
            expired_campaigns = db.query(campaign_model.Campaign).filter(
                campaign_model.Campaign.state == CampaignState.published,
                campaign_model.Campaign.effective_end_date != None,
                campaign_model.Campaign.effective_end_date < now_utc
            ).all()

            for campaign in expired_campaigns:
                if campaign.goal_amount and campaign.current_amount >= campaign.goal_amount:
                    campaign.state = CampaignState.success
                else:
                    campaign.state = CampaignState.fail

            if expired_campaigns:
                db.commit()
            
            db.close()
        except Exception as e:
            print(f"Error in expire_campaigns_task: {e}")
        
        # Run every 5 minutes
        await asyncio.sleep(300)

async def expire_edit_requests_task():
    while True:
        try:
            db = SessionLocal()
            now_utc = datetime.now(timezone.utc)
            
            expired_requests = db.query(edit_request_model.EditRequest).filter(
                edit_request_model.EditRequest.status == EditRequestStatus.pending,
                edit_request_model.EditRequest.expires_at != None,
                edit_request_model.EditRequest.expires_at < now_utc
            ).all()

            for req in expired_requests:
                req.status = EditRequestStatus.expired
                req.resolved_at = now_utc

            if expired_requests:
                db.commit()
            
            db.close()
        except Exception as e:
            print(f"Error in expire_edit_requests_task: {e}")
        
        # Run every 5 minutes
        await asyncio.sleep(300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: spawn the background tasks
    task1 = asyncio.create_task(expire_campaigns_task())
    task2 = asyncio.create_task(expire_edit_requests_task())
    yield
    # Shutdown: cancel the tasks
    task1.cancel()
    task2.cancel()

Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
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
app.include_router(campaign_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(media_router, prefix="/api")
app.include_router(country_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(comment_router, prefix="/api")
app.include_router(predict_router, prefix="/api")
app.include_router(notification_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(campaign_recommend_router, prefix="/api")
app.include_router(home_router, prefix="/api")
app.include_router(progress_router, prefix="/api")
app.include_router(edit_request_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(creator_router, prefix="/api")
app.include_router(contributor_router, prefix="/api")
app.include_router(bookmark_router, prefix="/api") # this comment is for image trigger