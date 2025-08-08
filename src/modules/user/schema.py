# modules/user/schema.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    clerk_id: str 
    username: str
    email: EmailStr
    first_name: Optional[str]
    middle_name: Optional[str]
    surname: Optional[str]
    address: Optional[str]
    tel: Optional[str]
    country: Optional[UUID]
    birth_date: Optional[date]
    image_id: Optional[UUID]
    user_description: Optional[str]

class UserOut(UserCreate):
    campaign_number: int
    contribution_number: int
