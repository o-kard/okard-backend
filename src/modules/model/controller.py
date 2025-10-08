from clerk_backend_api import Session
from fastapi import APIRouter, Depends
from src.database.db import get_db
import torch
import torch.nn.functional as F
from . import model, schema, service

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/")
async def predict(data: schema.InputData, db: Session = Depends(get_db)):
    results = await service.predict(db, data)
    return results
