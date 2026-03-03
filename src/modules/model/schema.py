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
    category_group: str
    has_video: bool
    has_photo: bool
    created_at: Optional[str] = None
    # current_amount: float

class PredictionResult(BaseModel):
    post_id: Optional[str] = None
    success_label: str
    risk_label: str
    days_to_state_label: str
    goal_eval_label: str
    stretch_label: str

    class Config:
        from_attributes = True
