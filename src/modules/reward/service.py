import os
from typing import List, Optional
import uuid
from fastapi import  UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.image import model as image_model, repo as image_repo, service as image_service
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
        db_reward = model.Reward(**data.model_dump())
        db.add(db_reward)
        db.commit()
        db.refresh(db_reward)

        await image_service._save_files_and_create_images(db, db_reward.id, files, parent_type="reward")

        db_rewards.append(db_reward)
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

    return db_reward


def delete_reward(db: Session, reward_id: UUID):
    db_reward = get_reward(db, reward_id)
    
    for image in list(db_reward.images):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)

    return repo.delete_reward(db, db_reward)
