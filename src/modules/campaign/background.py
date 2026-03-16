import json
from src.database.db import SessionLocal
from src.modules.campaign.model import Campaign, CampaignEmbedding
from src.modules.recommend.encoder import encode_texts

def generate_campaign_embedding(campaign_id):
    """
    Background job:
    - load campaign by id
    - build text from header/description/category
    - encode to embedding
    - save to campaign.embedding (JSON string)
    """
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return

        text = (
            f"{campaign.campaign_header}. "
            f"{campaign.campaign_description or ''}. "
            f"Category: {campaign.category.value if campaign.category else ''}."
        )

        emb = encode_texts([text])[0]
        emb_json = json.dumps(emb)

        if campaign.embedding_data:
            campaign.embedding_data.embedding = emb_json
        else:
            campaign.embedding_data = CampaignEmbedding(embedding=emb_json)
        
        db.commit()
    finally:
        db.close()
