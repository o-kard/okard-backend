from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.modules.user.service import get_user_by_clerk_id
from . import repo
from .schema import CreatorCreate, CreatorUpdate
from src.modules.common.enums import VerificationStatus, NotificationType
from src.modules.creator_verification_doc import repo as verification_doc_repo
from src.modules.notification import service as notification_service, schema as notification_schema

async def create_creator(db: Session, creator_data: CreatorCreate, clerk_id: str):
    """Create a new creator profile"""
    print("create_creator", clerk_id)
    user = await get_user_by_clerk_id(db, clerk_id)
    print("user", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if creator profile already exists
    existing_creator = repo.get_creator_by_user_id(db, user.id)
    if existing_creator:
        return repo.update_creator_on_resubmit(db, existing_creator, creator_data)
        
    return repo.create_creator(db, creator_data, user.id)

async def get_creator_by_id(db: Session, creator_id: UUID):
    """Get creator by ID"""
    return repo.get_creator_by_id(db, creator_id)

async def get_creator_by_clerk_id(db: Session, clerk_id: str):
    """Get creator by clerk_id"""
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        return None
    return repo.get_creator_by_user_id(db, user.id)

async def update_creator(db: Session, creator_id: UUID, creator_data: CreatorUpdate, clerk_id: str):
    """Update creator profile"""
    user = await get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    creator = repo.get_creator_by_id(db, creator_id)
    if not creator:
        raise ValueError("Creator not found")
    
    # Check if the user owns this creator profile
    if creator.user_id != user.id:
        raise PermissionError("You don't have permission to update this creator profile")
    
    return repo.update_creator(db, creator_id, creator_data)

def get_pending_creators(db: Session):
    """Get all creators awaiting verification"""
    return repo.get_pending_creators(db)

async def verify_creator_request(db: Session, creator_id: UUID, status: str, admin_clerk_id: str, rejection_reason: str = None):
    admin = await get_user_by_clerk_id(db, admin_clerk_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin user not found")
        
    try:
        enum_status = VerificationStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid verification status")
        
    creator = repo.update_verification_status(db, creator_id, enum_status, admin.id, rejection_reason)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
        
    if enum_status == VerificationStatus.verified:
        verification_doc_repo.verify_all_docs(db, creator.id, admin.id)
    elif enum_status == VerificationStatus.rejected:
        verification_doc_repo.delete_all_docs(db, creator.id)
        
    if enum_status in [VerificationStatus.verified, VerificationStatus.rejected]:
        status_text = "Approved" if enum_status == VerificationStatus.verified else "Rejected"
        message = f"Your creator verification request has been {status_text.lower()}."
        if enum_status == VerificationStatus.rejected and rejection_reason:
            message += f" Reason: {rejection_reason}"
            
        notif = notification_schema.NotificationCreate(
            user_id=creator.user_id,
            actor_id=admin.id,
            notification_title=f"Creator Request {status_text}",
            notification_message=message,
            type=NotificationType.system_alert
        )
        await notification_service.create_notification(db, notif)
        
    return creator
