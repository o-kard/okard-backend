import json
import numpy as np
from sqlalchemy.orm import Session
from uuid import UUID
from . import repo
from src.modules.campaign.repo import hydrate_campaign_bookmarks
from src.modules.user.service import get_user_by_clerk_id

async def recommend_by_campaign(db: Session, campaign_id: UUID, top_k: int = 5, clerk_id: str | None = None):
    source = repo.get_campaign_by_id(db, campaign_id)
    if not source:
        raise ValueError("Campaign not found")

    # ✅ fallback ถ้า embedding ยังไม่พร้อม
    if not source.embedding_data or not source.embedding_data.embedding:
        print(f"⚠️ [Recommendation] Fallback to same category for source: {source.campaign_header} ({source.id})")
        campaigns = repo.fallback_same_category(db, source, top_k)
        if clerk_id:
            user = await get_user_by_clerk_id(db, clerk_id)
            if user:
                hydrate_campaign_bookmarks(db, campaigns, user.id)
        return [{"campaign_id": p.id, "score": 0.0, "campaign": p} for p in campaigns]

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
    campaign_ids = [pid for pid, s in scored[:top_k]]
    campaign_objs = [repo.get_campaign_by_id(db, pid) for pid in campaign_ids]
    campaign_objs = [p for p in campaign_objs if p]

    print(f"\n✨ [Recommendation] Ranking for: {source.campaign_header} ({source.id})")
    for i, (p, (pid, s)) in enumerate(zip(campaign_objs, scored[:top_k])):
        if p:
            print(f"  Rank {i+1}: Score={s:.4f} | {p.campaign_header} ({pid})")
    print("-" * 50)

    # Hydrate bookmarks
    if clerk_id:
        user = await get_user_by_clerk_id(db, clerk_id)
        if user:
            hydrate_campaign_bookmarks(db, campaign_objs, user.id)

    results = []
    for p, (pid, s) in zip(campaign_objs, scored[:top_k]):
        results.append({
            "campaign_id": pid,
            "score": s,
            "campaign": p
        })
    return results
