import os
from typing import List
from dotenv import load_dotenv
import numpy as np

load_dotenv()

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class EmbeddingProvider:
    def __init__(self, model_name: str = MODEL_NAME):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        arr = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=False)
        arr = np.atleast_2d(arr).astype('float32')
        # return as list of floats
        return [a.tolist() for a in arr]


# Singleton provider
_provider: EmbeddingProvider | None = None


def get_provider() -> EmbeddingProvider:
    global _provider
    if _provider is None:
        _provider = EmbeddingProvider()
    return _provider
