# modules/user/controller.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from . import schema, service
from src.database.db import get_db

router = APIRouter(prefix="/country", tags=["Country"])

@router.get("", response_model=list[schema.CountryOut])
def list_country(db: Session = Depends(get_db)):
    return service.get_country_list(db)

@router.get("/{country_id}", response_model=schema.CountryOut)
def get_country(country_id: UUID, db: Session = Depends(get_db)):
    country = service.get_country(db, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

# Just in case
@router.put("/{country_id}", response_model=schema.CountryOut)
def update_country(country_id: UUID, data: schema.CountryBase, db: Session = Depends(get_db)):
    country = service.update_country(db, country_id, data)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country
