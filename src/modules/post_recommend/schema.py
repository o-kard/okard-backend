from pydantic import BaseModel
from uuid import UUID
from typing import List

class RecommendedPost(BaseModel):
    post_id: UUID
    score: float

class PostRecommendResponse(BaseModel):
    source_post_id: UUID
    recommendations: List[RecommendedPost]
