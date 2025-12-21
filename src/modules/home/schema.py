# src/modules/home/schema.py
from pydantic import BaseModel
from typing import List, Optional


class HomeImage(BaseModel):
    path: str


class HomeCreator(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None


class HomeCampaign(BaseModel):
    id: str
    user_id: str
    category: str

    post_header: str
    post_description: Optional[str] = None

    goal_amount: float
    current_amount: float
    progress: int

    images: List[HomeImage]
    creator: HomeCreator    
    supporter: int     

class CategoryStat(BaseModel):
    category: str
    total_projects: int
    funded_projects: int
    total_raised: float