# modules/user/schema.py
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from datetime import date
from typing import Optional
from src.modules.country.schema import CountryOut
from src.modules.media.schema import MediaOut
from src.modules.creator.schema import CreatorResponse

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    surname: Optional[str] = None
    address: Optional[str] = None
    tel: Optional[str] = None
    country_id: Optional[UUID] = None
    birth_date: Optional[date] = None

class UserCreate(UserBase):
    clerk_id: str
    pass
    
class UserUpdate(UserBase):
    remove_image: bool | None = None
    role: str | None = None
    pass

class UserResponse(UserBase):
    id: UUID
    contribution_number: int
    media: MediaOut | None = None
    country: CountryOut | None = None
    role: str | None = None
    creator: CreatorResponse | None = None
    
    class Config:
        from_attributes = True
        
class UserExistsResponse(BaseModel):
    exists: bool
    
    class Config:
        from_attributes = True
        
class UserPublicResponse(BaseModel):
    id: UUID
    username: str
    first_name: str | None = None
    surname: str | None = None
    user_description: str | None = None
    campaign_number: int | None = 0
    contribution_number: int | None = Field(default=0, validation_alias="total_backers")
    media: MediaOut | None = None
    
    class Config:
        from_attributes = True
        populate_by_name = True