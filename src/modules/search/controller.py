from src.modules.search.service import SearchService
from src.modules.search.schemas import SearchResponse
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.database.db import get_db

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", response_model=SearchResponse)
def search(query: str, request: Request, db: Session = Depends(get_db)):
    response = SearchService.search(db, query, request)
    response.results = response.results[:5]
    return response
