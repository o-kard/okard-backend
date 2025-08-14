# modules/user/schema.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import date
from typing import Optional

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
    image_id: Optional[UUID] = None
    user_description: Optional[str] = None

class UserOut(UserCreate):
    campaign_number: int
    contribution_number: int
