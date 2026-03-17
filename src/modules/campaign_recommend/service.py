import json
import numpy as np
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo

def recommend_by_campaign(db: Session, campaign_id: UUID, top_k: int = 5):
    source = repo.get_campaign_by_id(db, campaign_id)
    if not source:
        raise ValueError("Campaign not found")

    # ✅ fallback ถ้า embedding ยังไม่พร้อม
    if not source.embedding_data or not source.embedding_data.embedding:
        campaigns = repo.fallback_same_category(db, source, top_k)
        return [{"campaign_id": p.id, "score": 0.0} for p in campaigns]

    source_vec = np.array(json.loads(source.embedding_data.embedding))

    candidates = repo.list_candidates(db, source)

    scored = []
    for p in candidates:
        try:
            if not p.embedding_data or not p.embedding_data.embedding:
                continue
            vec = np.array(json.loads(p.embedding_data.embedding))
            score = float(vec @ source_vec) 
            scored.append((p.id, score))
        except Exception:
            continue

    scored.sort(key=lambda x: x[1], reverse=True)
    return [{"campaign_id": pid, "score": s} for pid, s in scored[:top_k]]
