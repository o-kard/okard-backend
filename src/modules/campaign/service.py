import os
from typing import List, Optional
import uuid
from fastapi import  UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo, schema, model
from src.modules.image import model as image_model, repo as image_repo
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
        db_campaign = model.Campaign(**data.model_dump())
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)

        for file in files:
            content = await file.read()
            ext = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4().hex}{ext}"
            file_path = UPLOAD_DIR / file_name

            with open(file_path, "wb") as f:
                f.write(content)

            image = image_model.Image(
                id=uuid.uuid4(),
                campaign_id=db_campaign.id,
                orig_name=file.filename,
                media_type=file.content_type,
                file_size=len(content),
                path=f"/uploads/images/{file_name}"
            )
            image_repo.create_image(db, image)

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
        db.delete(image)
    db.commit()

    for file in files:
        content = await file.read()
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4().hex}{ext}"
        with open(UPLOAD_DIR / file_name, "wb") as f:
            f.write(content)

        image = image_model.Image(
            id=uuid.uuid4(),
            campaign_id=db_campaign.id,
            orig_name=file.filename,
            media_type=(file.content_type or "application/octet-stream"),
            file_size=len(content),
            path=f"/uploads/images/{file_name}"
        )
        image_repo.create_image(db, image)

    return db_campaign



def delete_campaign(db: Session, campaign_id: UUID):
    db_campaign = get_campaign(db, campaign_id)
    
    for image in list(db_campaign.images):
        if image.path:
            ap = _abs(image.path)
            if os.path.exists(ap):
                os.remove(ap)

    return repo.delete_campaign(db, db_campaign)
