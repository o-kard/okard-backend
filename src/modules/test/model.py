import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from src.database.db import Base

class Test(Base):
    __tablename__ = "tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
