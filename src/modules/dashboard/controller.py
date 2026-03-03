from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from . import service, schema

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=schema.UserDashboardSummary)
async def user_summary(clerk_id: str = Query(...), db: Session = Depends(get_db)):
    return await service.get_user_dashboard(db, clerk_id)

@router.get("/posts", response_model=list[schema.PostProgress])
async def user_posts_progress(
    clerk_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return await service.get_post_progress(db, clerk_id, limit, offset)

@router.get("/payments", response_model=list[schema.PaymentDailyStat])
async def user_payment_stats(
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return await service.get_payment_stats(db, clerk_id)


@router.get("/investors-by-country", response_model=list[schema.InvestorCountryStat])
async def investors_by_country(
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return await service.get_investor_country_stats(db, clerk_id)

@router.get("/posts/trending", response_model=list[schema.TrendingPost])
async def get_trending_posts(
    day: date = date.today(),
    db: Session = Depends(get_db),
    clerk_id: str = Query(...)
):
    return await service.list_trending_posts(db, day, clerk_id)