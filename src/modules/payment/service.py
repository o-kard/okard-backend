# src/modules/payment/service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from . import repo, schema, model
from src.modules.contributor import service as contributor_service
from src.modules.reward import service as reward_service
from src.modules.campaign import repo as campaign_repo
from src.modules.common.enums import CampaignState
from datetime import datetime, timezone

from src.modules.notification import service as notification_service
from src.modules.notification import schema as notification_schema
from src.modules.common.enums import NotificationType

def list_payments(db: Session) -> List[model.Payment]:
    return repo.list_payments(db)

def get_payment(db: Session, payment_id: UUID) -> model.Payment:
    db_payment = repo.get_payment(db, payment_id)
    if not db_payment:
        raise ValueError("Payment not found")
    return db_payment

async def create_payment(db: Session, clerk_id: str, data: schema.PaymentCreate) -> model.Payment:
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    payload = data

    campaign = campaign_repo.get_campaign(db, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if campaign is expired
    if campaign.effective_end_date:
        now_utc = datetime.now(timezone.utc)
        if now_utc > campaign.effective_end_date:
            raise HTTPException(status_code=400, detail="This campaign has ended and is no longer accepting payments.")

    if campaign.state == CampaignState.draft:
        raise HTTPException(status_code=400, detail="This campaign is still a draft and is not accepting payments.")
    if campaign.state == CampaignState.fail:
        raise HTTPException(status_code=400, detail="This campaign has failed and is no longer accepting payments.")
    if campaign.state == CampaignState.suspend:
        raise HTTPException(status_code=400, detail="This campaign is suspended and is not accepting payments.")

    prev_amount = campaign.current_amount 
    goal_amount = campaign.goal_amount 

    db_payment = repo.create_payment(db, payload, user_id=user.id)

    _, is_new_contributor = contributor_service.ensure_and_add_amount(
        db=db,
        user_id=user.id,
        campaign_id=payload.campaign_id,
        amount=payload.amount,
    )

    if is_new_contributor:
        campaign_repo.increment_supporter(db, payload.campaign_id)

    campaign_repo.increment_current_amount(
        db=db,
        campaign_id=payload.campaign_id,
        delta=payload.amount
    )

    reward_service.calculate_backup_amounts_for_campaign(db=db, campaign_id=payload.campaign_id)

    new_amount = prev_amount + payload.amount

    # Auto-Success check
    if goal_amount and new_amount >= goal_amount and campaign.state == CampaignState.published:
        campaign_repo.update_campaign_state(db, campaign, CampaignState.success)

    if goal_amount and prev_amount < goal_amount <= new_amount:
        # Notify Creator
        notif = notification_schema.NotificationCreate(
            user_id=campaign.user_id,             
            actor_id=user.id,                
            campaign_id=campaign.id,
            notification_title="🎉 Goal reached!",
            notification_message=(
                f"Your campaign \"{campaign.campaign_header}\" has reached its goal of {goal_amount}."
            ),
            type=NotificationType.goal,
        )
        await notification_service.create_notification(db, notif)
        
        # Notify Supporters
        contributors = contributor_service.repo.list_contributors_by_campaign(db, campaign.id)
        supporter_ids = set([c.user_id for c in contributors if c.user_id != campaign.user_id])
        for s_id in supporter_ids:
            s_notif = notification_schema.NotificationCreate(
                user_id=s_id,
                actor_id=user.id,
                campaign_id=campaign.id,
                notification_title="🚀 Campaign Funded!",
                notification_message=f"A campaign you supported '{campaign.campaign_header}' has reached its goal!",
                type=NotificationType.goal,
            )
            await notification_service.create_notification(db, s_notif)

    return db_payment

def delete_payment(db: Session, payment_id: UUID) -> model.Payment:
    db_payment = get_payment(db, payment_id)
    return repo.delete_payment(db, db_payment)
