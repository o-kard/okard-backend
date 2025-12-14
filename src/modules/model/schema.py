# Pydantic models for validation (requests and responses)
from typing import Optional
from pydantic import BaseModel

class InputData(BaseModel):
    goal: float
    name: str
    blurb: str
    start_date: str   
    end_date: str     
    country_displayable_name: str
    has_video: int
    has_photo: int
    # current_amount: float

class PredictionResult(BaseModel):
    post_id: Optional[str] = None
    success_label: str
    risk_label: str
    days_to_state_label: str
    category_label: str
    goal_eval_label: str
    stretch_label: str

    class Config:
        orm_mode = True
