from typing import List, Tuple
import numpy as np


def cosine_sim(a: List[float], b: List[float]) -> float:
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_most_similar(query_vec: List[float], candidates: List[Tuple[int, List[float]]], top_k: int = 5):
    # candidates: list of (id, embedding)
    scores = []
    for cid, emb in candidates:
        if emb is None:
            continue
        scores.append((cid, cosine_sim(query_vec, emb)))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]
