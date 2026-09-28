import os
import faiss
import numpy as np
from typing import List, Tuple

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "incidents.index")
MAPPING_PATH = os.path.join(os.path.dirname(__file__), "..", "incidents.mapping.npy")


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.id_map = []  # list of incident ids in same order as index

    def add(self, incident_id: int, vector: List[float]):
        v = np.array(vector, dtype='float32').reshape(1, -1)
        # normalize for cosine via inner product
        faiss.normalize_L2(v)
        self.index.add(v)
        self.id_map.append(incident_id)

    def search(self, vector: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        q = np.array(vector, dtype='float32').reshape(1, -1)
        faiss.normalize_L2(q)
        if self.index.ntotal == 0:
            return []
        D, I = self.index.search(q, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.id_map):
                continue
            results.append((self.id_map[idx], float(score)))
        return results

    def save(self, path: str | None = None):
        p = path or INDEX_PATH
        faiss.write_index(self.index, p)
        np.save(MAPPING_PATH, np.array(self.id_map, dtype=np.int64))

    def load(self, path: str | None = None):
        p = path or INDEX_PATH
        if os.path.exists(p):
            self.index = faiss.read_index(p)
            self.id_map = np.load(MAPPING_PATH).tolist()


# Singleton
_store: VectorStore | None = None


def get_store(dim: int) -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(dim)
        try:
            _store.load()
        except Exception:
            # empty index is fine
            pass
    return _store
