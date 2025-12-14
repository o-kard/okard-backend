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

def list_campaigns(db: Session):
    # print(UPLOAD_DIR)
    return repo.list_campaigns(db)

def get_campaign(db: Session, campaign_id: UUID):
    campaign = repo.get_campaign(db, campaign_id)
    if not campaign:
        raise ValueError("Campaign not found")
    return campaign

def update_campaign(db: Session, campaign_id: UUID, campaign_data: schema.CampaignUpdate):
    db_campaign = get_campaign(db, campaign_id)
    return repo.update_campaign(db, db_campaign, campaign_data)


async def create_campaign_with_images(
    db: Session,
    campaign_data: List[schema.CampaignCreate],
    files: List[UploadFile]
):
    db_campaigns = []
    for data in campaign_data:
        db_campaign = repo.create_campaign(db, data)
        await image_service._save_files_and_create_images(
            db,
            parent_type="campaign",
            parent_id=db_campaign.id,
            files=files,                       
            images_manifest=None,             
        )
        db_campaigns.append(db_campaign)
    return db_campaigns



# campaign/service.py
async def update_campaign_with_images(db: Session, campaign_id: UUID,
                                      campaign_data: schema.CampaignUpdate,
                                      files: Optional[List[UploadFile]] = None):
    db_campaign = get_campaign(db, campaign_id)

    repo.update_campaign(db, db_campaign, campaign_data)

    if not files:
        return db_campaign

    for image in list(db_campaign.images):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)
        image_repo.delete_image(db, image)
    db.commit()

    await image_service._save_files_and_create_images(
        db,
        parent_type="campaign",
        parent_id=db_campaign.id,
        files=files,
        images_manifest=None
    )

    return db_campaign



def delete_campaign(db: Session, campaign_id: UUID):
    db_campaign = get_campaign(db, campaign_id)
    
    for image in list(db_campaign.images):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)
        image_repo.delete_image(db, image)

    return repo.delete_campaign(db, db_campaign)
