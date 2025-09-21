# modules/user/schema.py
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import date
from typing import Optional
from src.modules.country.schema import CountryOut
from src.modules.image.schema import ImageOut

class UserBase(BaseModel):
    clerk_id: str 
    username: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    surname: Optional[str] = None
    address: Optional[str] = None
    tel: Optional[str] = None
    country_id: Optional[UUID] = None
    birth_date: Optional[date] = None
    user_description: Optional[str] = None

class UserCreate(UserBase):
    pass
    
class UserUpdate(UserBase):
    remove_image: bool | None = None
    pass

class UserResponse(UserBase):
    id: UUID
    campaign_number: int
    contribution_number: int
    image: ImageOut | None = None
    country: CountryOut | None = None
    
    class Config:
        orm_mode = True
        
class UserExistsResponse(BaseModel):
    exists: bool
    
    class Config:
        orm_mode = True
        
class UserPublicResponse(BaseModel):
    id: UUID
    username: str
    image: ImageOut | None = None
    
    class Config:
        orm_mode = True