import json
from src.database.db import SessionLocal
from src.modules.post.model import Post
from src.modules.recommend.encoder import encode_texts

def generate_post_embedding(post_id):
    """
    Background job:
    - load post by id
    - build text from header/description/category
    - encode to embedding
    - save to post.embedding (JSON string)
    """
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return

        text = (
            f"{post.post_header}. "
            f"{post.post_description or ''}. "
            f"Category: {post.category.value if post.category else ''}."
        )

        emb = encode_texts([text])[0]
        post.embedding = json.dumps(emb)
        db.commit()
    finally:
        db.close()
