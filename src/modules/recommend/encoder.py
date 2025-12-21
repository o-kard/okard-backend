from typing import List
from .model import get_embedding_model

def encode_texts(texts: List[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
