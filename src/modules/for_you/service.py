import json
import numpy as np
from datetime import datetime, timezone
import random
from sqlalchemy.orm import Session

from src.database import db

from .repo import (
    get_recent_viewed_campaign_embeddings,
    get_seen_campaign_ids,
    get_candidate_campaign_embeddings,
    get_fallback_popular_campaign_ids,
    get_campaigns_by_ids,
    get_user_category_affinity,
)

# from src.modules.home.service import map_campaign_to_home


def _normalize(vec: np.ndarray):
    norm = np.linalg.norm(vec)
    if norm == 0:
        return None
    return vec / norm


def _build_user_vector(db: Session, user_id, limit: int = 20):
    rows = get_recent_viewed_campaign_embeddings(db, user_id, limit)

    if not rows:
        return None

    seen_campaigns = set()
    vecs = []

    for pid, emb in rows:
        if pid in seen_campaigns:
            continue
        seen_campaigns.add(pid)

        try:
            v = np.array(json.loads(emb), dtype=np.float32)
            v = _normalize(v)
            if v is not None:
                vecs.append(v)
        except Exception:
            continue

    if not vecs:
        return None

    weights = np.exp(-0.3 * np.arange(len(vecs)))
    weights = weights / weights.sum()

    user_vec = np.sum(
        np.stack(vecs) * weights[:, None],
        axis=0
    )
    user_vec = _normalize(user_vec)

    return _normalize(user_vec)

def popularity_score(campaign):
    return np.log1p(campaign.supporter) / np.log1p(2) #จำนวน supporter max score

def freshness_boost(campaign, half_life_days: int = 14) -> float:
    age_days = (datetime.now(timezone.utc) - campaign.created_at).days
    return np.exp(-age_days / half_life_days)

def diversity_penalty(
    campaign,
    recent_campaigns,
    penalty: float = 0.15
) -> float:
    if not recent_campaigns:
        return 0.0

    recent_categories = [p.category for p in recent_campaigns]
    if campaign.category in recent_categories:
        return penalty

    return 0.0


def inject_exploration(scored, explore_rate=0.15):
    if len(scored) < 3:
        return scored

    k = max(1, int(len(scored) * explore_rate))
    tail = scored[len(scored)//2:]
    explore = random.sample(tail, min(k, len(tail)))

    head = scored[:len(scored) - len(explore)]
    mixed = head + explore
    random.shuffle(mixed)

    return mixed


def for_you(db: Session, user_id, limit: int = 10):
    MIN_SCORE = 0.15

    user_vec = _build_user_vector(db, user_id)

    if user_vec is None:
        campaign_ids = get_fallback_popular_campaign_ids(db, limit)
        campaigns = get_campaigns_by_ids(db, campaign_ids)

        return [
            {"campaign": p, "score": 0.0}
            for p in campaigns
        ]

    seen_ids = get_seen_campaign_ids(db, user_id)
    candidates = get_candidate_campaign_embeddings(db, user_id)
    affinity = get_user_category_affinity(db, user_id)

    candidate_ids = [pid for pid, _ in candidates]
    campaigns = get_campaigns_by_ids(db, candidate_ids)
    campaign_map = {p.id: p for p in campaigns}

    scored = []

    for pid, emb in candidates:
        if pid in seen_ids:
            continue

        campaign = campaign_map.get(pid)
        if not campaign:
            continue

        try:
            vec = np.array(json.loads(emb), dtype=np.float32)
            vec = _normalize(vec)
            if vec is None:
                continue

            semantic = float(np.dot(vec, user_vec))
            cat_score = affinity.get(campaign.category, 0.0)
            pop_score = popularity_score(campaign)
            fresh_score = freshness_boost(campaign)

            score = (
                0.55 * semantic +
                0.20 * cat_score +
                0.15 * pop_score +
                0.10 * fresh_score
            )

            if score < MIN_SCORE:
                continue

            scored.append((pid, score))

        except Exception:
            continue

    scored.sort(key=lambda x: x[1], reverse=True)

    final = []
    used_ids = set()
    recent_campaigns = []

    for pid, score in scored:
        if pid in used_ids:
            continue

        campaign = campaign_map.get(pid)
        if not campaign:
            continue

        penalty = diversity_penalty(campaign, recent_campaigns)
        final_score = score - penalty

        final.append((pid, final_score))
        used_ids.add(pid)
        recent_campaigns.append(campaign)

        if len(final) >= limit * 2:
            break

    final.sort(key=lambda x: x[1], reverse=True)

    dedup = []
    seen = set()
    for pid, score in final:
        if pid in seen:
            continue
        dedup.append((pid, score))
        seen.add(pid)

    top_candidates = dedup[:limit]
    mixed_results = inject_exploration(top_candidates, explore_rate=0.15)

    return [
        {
            "campaign": campaign_map[pid],
            "score": score,
        }
        for pid, score in mixed_results
    ]



