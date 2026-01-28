import json
import numpy as np
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo

def recommend_by_post(db: Session, post_id: UUID, top_k: int = 5):
    source = repo.get_post_by_id(db, post_id)
    if not source:
        raise ValueError("Post not found")

    # ✅ fallback ถ้า embedding ยังไม่พร้อม
    if not source.embedding_data or not source.embedding_data.embedding:
        posts = repo.fallback_same_category(db, source, top_k)
        return [{"post_id": p.id, "score": 0.0} for p in posts]

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
    return [{"post_id": pid, "score": s} for pid, s in scored[:top_k]]
