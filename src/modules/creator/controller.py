import json
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from fastapi.params import Query
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.modules.auth import get_current_user
from . import service, schema
from src.modules.user import schema as userSchema
from src.modules.user import service as userService
from src.modules.media import service as mediaService
from src.modules.creator_verification_doc import service as verificationDocService
from src.modules.common.enums import UserRole, VerificationDocType

router = APIRouter(prefix="/creator", tags=["Creator"])

@router.post("", response_model=schema.CreatorCreateResponse)
async def create_creator(
    data: str = Form(...),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
    image: Optional[UploadFile] = File(None),
    id_card: Optional[UploadFile] = File(None),
    house_registration: Optional[UploadFile] = File(None),
    bank_statement: Optional[UploadFile] = File(None),
):
    """Create a new creator profile with user update"""
    print("data", data)
    print("image", image)
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid JSON format: {str(e)}. Please check your JSON syntax."
        )
        
    try:
        creator_obj = schema.CreatorCreate(**parsed_data['creator'])
        user_obj = userSchema.UserUpdate(**parsed_data['user'])
        remove_image = user_obj.remove_image
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user data: {str(e)}")
    
    clerk_id = payload["sub"]
    
    try:
        user = await userService.get_user_by_clerk_id(db, clerk_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Set user role to creator
        user_obj.role = UserRole.creator
        user_res = await userService.update_profile(db, clerk_id, user_obj)
        
        # Step 2: Handle image upload/deletion
        if image:
            await imageService.create_image_from_upload(
                db, 
                file=image,
                clerk_id=user_res.clerk_id
            )
        elif remove_image and user_res.image:
            await imageService.delete_image(db, user_res.image.id)
        
        # Step 3: Create creator profile
        creator_res = await service.create_creator(db, creator_obj, clerk_id)
        
        # Step 4: Handle verification document uploads
        if id_card:
            await verificationDocService.create_verification_doc_from_upload(
                db=db,
                creator_id=creator_res.id,
                doc_type=VerificationDocType.id_card,
                file=id_card
            )
        
        if house_registration:
            await verificationDocService.create_verification_doc_from_upload(
                db=db,
                creator_id=creator_res.id,
                doc_type=VerificationDocType.house_registration,
                file=house_registration
            )
        
        if bank_statement:
            await verificationDocService.create_verification_doc_from_upload(
                db=db,
                creator_id=creator_res.id,
                doc_type=VerificationDocType.bank_statement,
                file=bank_statement
            )
        
        # Success: return minimal response
        return schema.CreatorCreateResponse(
            success=True,
            message="Creator profile created successfully",
            creator_id=creator_res.id,
            user_id=creator_res.user_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create creator: {str(e)}")

@router.get("/me", response_model=schema.CreatorOut)
async def get_my_creator_profile(
    clerk_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Get the creator profile for the authenticated user"""
    creator = service.get_creator_by_clerk_id(db, clerk_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    return creator

@router.get("/{creator_id}", response_model=schema.CreatorOut)
async def get_creator(
    creator_id: UUID,
    db: Session = Depends(get_db),
):
    """Get creator by ID"""
    creator = service.get_creator_by_id(db, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator

@router.put("/{creator_id}", response_model=schema.CreatorOut)
async def update_creator(
    creator_id: UUID,
    creator_data: schema.CreatorUpdate,
    db: Session = Depends(get_db),
    clerk_id: str = Query(...),
):
    """Update creator profile"""
    try:
        return service.update_creator(db, creator_id, creator_data, clerk_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
