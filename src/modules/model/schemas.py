from pydantic import BaseModel

class InputData(BaseModel):
    goal: float
    name: str
    blurb: str
    start_date: str   # yyyy-mm-dd
    end_date: str     # yyyy-mm-dd
    currency: str
    country_displayable_name: str
    location_state: str
    has_video: int
    has_photo: int
    # dur_bin: str
