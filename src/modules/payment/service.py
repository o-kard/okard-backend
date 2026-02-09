# src/modules/payment/service.py
from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from . import repo, schema, model
from src.modules.contributor import service as contributor_service
from src.modules.reward import service as reward_service
from src.modules.post import repo as post_repo

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

    post = post_repo.get_post(db, payload.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    prev_amount = post.current_amount 
    print(prev_amount)
    goal_amount = post.goal_amount 

    db_payment = repo.create_payment(db, payload, user_id=user.id)

    _, is_new_contributor = contributor_service.ensure_and_add_amount(
        db=db,
        user_id=user.id,
        post_id=payload.post_id,
        amount=payload.amount,
    )

    if is_new_contributor:
        post_repo.increment_supporter(db, payload.post_id)

    post_repo.increment_current_amount(
        db=db,
        post_id=payload.post_id,
        delta=payload.amount
    )

    reward_service.calculate_backup_amounts_for_post(db=db, post_id=payload.post_id)

    new_amount = prev_amount + payload.amount

    if goal_amount and prev_amount < goal_amount <= new_amount:
        notif = notification_schema.NotificationCreate(
            user_id=post.user_id,             
            actor_id=user.id,                
            post_id=post.id,
            notification_title="🎉 Goal reached!",
            notification_message=(
                f"Your post \"{post.post_header}\" has reached its goal of {goal_amount}."
            ),
            type=NotificationType.goal,
        )
        await notification_service.create_notification(db, notif)

    return db_payment

def delete_payment(db: Session, payment_id: UUID) -> model.Payment:
    db_payment = get_payment(db, payment_id)
    return repo.delete_payment(db, db_payment)
