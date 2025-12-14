import os
from typing import List, Optional
import uuid
from fastapi import  UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.image import  service as image_service
from src.modules.contributor import model as contributor_model
from pathlib import Path
import os
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _abs(rel: str) -> str:
   return (BASE_DIR / rel.lstrip("/")).as_posix()

def list_rewards(db: Session):
    # print(UPLOAD_DIR)
    return repo.list_rewards(db)

def get_reward(db: Session, reward_id: UUID):
    reward = repo.get_reward(db, reward_id)
    if not reward:
        raise ValueError("Reward not found")
    return reward

def update_reward(db: Session, reward_id: UUID, reward_data: schema.RewardUpdate):
    db_reward = get_reward(db, reward_id)
    return repo.update_reward(db, db_reward, reward_data)


async def create_reward_with_images(
    db: Session,
    reward_data: List[schema.RewardCreate],
    files: List[UploadFile]
):
    db_rewards = []
    for data in reward_data:
        db_reward = repo.create_reward(db, data)
        await image_service._save_files_and_create_images(
            db,
            parent_type="reward",
            parent_id=db_reward.id,
            files=files,                       
            images_manifest=None,              
        )

        db_rewards.append(db_reward)

    if db_rewards:
        calculate_backup_amounts_for_post(db, db_rewards[0].post_id)

    return db_rewards

async def update_reward_with_images(
    db: Session,
    reward_id: UUID,
    reward_data: schema.RewardUpdate,
    files: Optional[List[UploadFile]] = None
):
    db_reward = get_reward(db, reward_id)
    repo.update_reward(db, db_reward, reward_data)

    if not files:
        return db_reward

    for image in list(db_reward.image):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)
        db.delete(image)
    db.commit()
    

    await image_service._save_files_and_create_images(db, db_reward.id, files, parent_type="reward")
    calculate_backup_amounts_for_post(db, db_reward.post_id)

    return db_reward


def delete_reward(db: Session, reward_id: UUID):
    db_reward = get_reward(db, reward_id)
    
    for image in list(db_reward.images):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)
    
    calculate_backup_amounts_for_post(db, db_reward.post_id)
    return repo.delete_reward(db, db_reward)

def calculate_backup_amounts_for_post(db: Session, post_id: UUID):
    repo.calculate_backup_amounts_for_post(db, post_id)