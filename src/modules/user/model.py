from sqlalchemy import Column, String, Date, Integer, ForeignKey, and_
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
    # password removed as per schema request (Clerk auth)
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
    
    posts = relationship("Post", back_populates="user")

    image = relationship(
        "Image",
        secondary="imageHandler",
        primaryjoin="and_(User.id==ImageHandler.reference_id, ImageHandler.type=='user')",
        secondaryjoin="ImageHandler.image_id==Image.id",
        uselist=False,
        viewonly=True,
    )
    country = relationship("Country", back_populates="users")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")