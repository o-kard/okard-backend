# modules/country/model.py
from datetime import datetime
from sqlalchemy import CHAR, Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from src.database.db import Base

class Country(Base):
    __tablename__ = "country"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    en_name = Column(String, nullable=False)
    alpha2 = Column(CHAR(5), nullable=False, unique=True)
    alpha3 = Column(CHAR(5), nullable=False, unique=True)
    numeric = Column(CHAR(3), nullable=False, unique=True)
    iso3166_2 = Column(String)
    enabled = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
