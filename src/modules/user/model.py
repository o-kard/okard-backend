# modules/user/model.py
from sqlalchemy import Column, String, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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
    country_id = Column(UUID(as_uuid=True), ForeignKey("country.id"), nullable=True)
    birth_date = Column(Date)
    user_description = Column(String)
    campaign_number = Column(Integer, default=0)
    contribution_number = Column(Integer, default=0)
    
    image = relationship("Image", back_populates="user", cascade="all, delete-orphan", uselist=False, single_parent=True)
    country = relationship("Country", back_populates="users")
