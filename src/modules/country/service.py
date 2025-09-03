# modules/user/service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from . import model, schema, repo

def get_country_list(db: Session) -> List[model.Country]:
    """ดึงรายการประเทศที่ enabled ทั้งหมด"""
    return repo.get_countries(db)

def get_country(db: Session, country_id: UUID) -> Optional[model.Country]:
    """ดึงข้อมูลประเทศตาม id"""
    return repo.get_country_by_id(db, country_id)

#Just in case
def update_country(db: Session, country_id: UUID, data: schema.CountryBase) -> Optional[model.Country]:
    """อัปเดตข้อมูลประเทศ"""
    country = repo.get_country_by_id(db, country_id)
    if not country:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(country, key, value)
    db.commit()
    db.refresh(country)
    return country