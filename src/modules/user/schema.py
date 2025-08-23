# modules/user/schema.py
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import date
from typing import Optional
from src.modules.image.schema import ImageOut

class UserCreate(BaseModel):
    clerk_id: str 
    username: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    surname: Optional[str] = None
    address: Optional[str] = None
    tel: Optional[str] = None
    country: Optional[UUID] = None
    birth_date: Optional[date] = None
    user_description: Optional[str] = None

class UserOut(UserCreate):
    id: UUID
    campaign_number: int
    contribution_number: int
    image: ImageOut | None = None
    
    class Config:
        orm_mode = True
        
class ExistsOut(BaseModel):
    exists: bool
    
    class Config:
        orm_mode = True