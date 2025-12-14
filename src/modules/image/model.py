import uuid
from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Enum, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.db import Base
from src.modules.common.enums import ReferenceType

class Image(Base):
    __tablename__ = "image"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_order = Column(Integer, nullable=False, default=0)
    orig_name = Column(String)
    media_type = Column(String)
    file_size = Column(BigInteger)
    path = Column(String)

class ImageHandler(Base):
    __tablename__ = "imageHandler"

    image_id = Column(UUID(as_uuid=True), ForeignKey("image.id"), primary_key=True)
    reference_id = Column(UUID(as_uuid=True), primary_key=True)
    type = Column(Enum(ReferenceType), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint('image_id', 'reference_id', 'type'),
    )

    image = relationship("Image")
