import os
import numpy as np
from typing import List, Tuple

try:
    import faiss
    _has_faiss = True
except Exception:
    faiss = None
    _has_faiss = False

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "incidents.index")
MAPPING_PATH = os.path.join(os.path.dirname(__file__), "..", "incidents.mapping.npy")


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.id_map: List[int] = []
        if _has_faiss:
            self.index = faiss.IndexFlatIP(dim)
        else:
            # fallback: keep numpy matrix
            self.vectors = np.zeros((0, dim), dtype='float32')

    def add(self, incident_id: int, vector: List[float]):
        v = np.array(vector, dtype='float32').reshape(1, -1)
        # normalize for cosine via inner product
        v_norm = v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)
        if _has_faiss:
            faiss.normalize_L2(v_norm)
            self.index.add(v_norm)
        else:
            self.vectors = np.vstack([self.vectors, v_norm])
        self.id_map.append(int(incident_id))

    def search(self, vector: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        q = np.array(vector, dtype='float32').reshape(1, -1)
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        results = []
        if _has_faiss:
            faiss.normalize_L2(q)
            if self.index.ntotal == 0:
                return []
            D, I = self.index.search(q, top_k)
            for score, idx in zip(D[0], I[0]):
                if idx < 0 or idx >= len(self.id_map):
                    continue
                results.append((self.id_map[idx], float(score)))
        else:
            if self.vectors.shape[0] == 0:
                return []
            sims = (self.vectors @ q.T).reshape(-1)
            idxs = np.argsort(-sims)[:top_k]
            for idx in idxs:
                results.append((self.id_map[idx], float(sims[idx])))
        return results

    def save(self, path: str | None = None):
        if _has_faiss:
            p = path or INDEX_PATH
            faiss.write_index(self.index, p)
        np.save(MAPPING_PATH, np.array(self.id_map, dtype=np.int64))

    def load(self, path: str | None = None):
        p = path or INDEX_PATH
        if os.path.exists(MAPPING_PATH):
            self.id_map = np.load(MAPPING_PATH).tolist()
        if _has_faiss and os.path.exists(p):
            self.index = faiss.read_index(p)
        else:
            # if mapping exists but no faiss index, we cannot restore vectors from FAISS binary.
            # vectors will be rebuilt from DB on startup if needed.
            pass


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
