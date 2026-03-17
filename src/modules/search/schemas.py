from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class SearchResult(BaseModel):
    id: UUID
    type: str    # "user" | "campaign"
    name: str
    thumbnail: Optional[str] = None
    creator: Optional[str] = None
    
class SearchResponse(BaseModel):
    results: list[SearchResult]
