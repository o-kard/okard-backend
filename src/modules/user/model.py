# modules/user/model.py
from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from src.database.db import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    clerk_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    first_name = Column(String)
    middle_name = Column(String)
    surname = Column(String)
    address = Column(String)
    tel = Column(String)
    country = Column(UUID(as_uuid=True), nullable=True)
    birth_date = Column(Date)
    image_id = Column(UUID(as_uuid=True), nullable=True)
    user_description = Column(String)
    campaign_number = Column(Integer, default=0)
    contribution_number = Column(Integer, default=0)
