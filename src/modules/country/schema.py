# modules/user/schema.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date
from typing import Optional

class CountryBase(BaseModel):
    name: str
    en_name: str
    alpha2: str
    alpha3: str
    numeric: Optional[str]
    iso3166_2: str

class CountryOut(CountryBase):
    id: UUID

    class Config:
        orm_mode = True