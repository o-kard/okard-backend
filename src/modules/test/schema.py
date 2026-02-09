# schema.py
from pydantic import BaseModel
from uuid import UUID


class TestBase(BaseModel):
    title: str
    description: str

class TestCreate(TestBase):
    pass

class TestUpdate(TestBase):
    pass

class TestOut(TestBase):
    id: UUID

    class Config:
        from_attributes = True
