"""Embedding-backed semantic search with OpenAI fallback to sentence-transformers.

If OPENAI_API_KEY is set in environment, use OpenAI embeddings via openai package.
Otherwise fall back to sentence-transformers local model (all-MiniLM-L6-v2).

Provides:
- index_logs(logs): builds a vector index (FAISS) and stores metadata
- query_index(query, top_k): returns top_k matching log entries
"""
from typing import List, Dict, Optional
import os

try:
    import numpy as np
except Exception:
    np = None

# Try OpenAI
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))

if USE_OPENAI:
    try:
        import openai
    except Exception:
        openai = None
else:
    openai = None

# Try sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

# Try FAISS
try:
    import faiss
except Exception:
    faiss = None

class SemanticIndex:
    def __init__(self, logs: List[Dict]):
        self.logs = logs
        self.embeddings = None
        self.index = None
        self._model = None

    def _get_model(self):
        if USE_OPENAI:
            return "openai"
        if SentenceTransformer is not None:
            if self._model is None:
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            return self._model
        raise RuntimeError("No embedding model available. Install openai or sentence-transformers.")

    def build(self):
        texts = [l.get("text", "") for l in self.logs]
        model = self._get_model()
        if USE_OPENAI and openai is not None:
            # Use OpenAI embeddings
            res = openai.Embedding.create(input=texts, model="text-embedding-3-small")
            embs = [r["embedding"] for r in res.data]
            self.embeddings = np.array(embs).astype("float32")
        else:
            if SentenceTransformer is None:
                raise RuntimeError("sentence-transformers not installed")
            embs = model.encode(texts, show_progress_bar=False)
            self.embeddings = np.array(embs).astype("float32")

        # Build FAISS index if available, else keep numpy array
        if faiss is not None:
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(self.embeddings)
        else:
            self.index = None

    def query(self, query: str, top_k: int = 5):
        model = self._get_model()
        if USE_OPENAI and openai is not None:
            qres = openai.Embedding.create(input=[query], model="text-embedding-3-small")
            qvec = np.array(qres.data[0]["embedding"]).astype("float32")
        else:
            qvec = model.encode([query])[0].astype("float32")

        if self.index is not None:
            D, I = self.index.search(np.array([qvec]), top_k)
            results = [self.logs[int(i)] for i in I[0] if i != -1]
            return results
        else:
            # fallback to cosine similarity with numpy
            if np is None:
                raise RuntimeError("Numpy not installed")
            embs = self.embeddings
            # cosine similarity
            def cos(a, b):
                return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))
            scores = [(cos(qvec, embs[i]), i) for i in range(len(embs))]
            scores.sort(key=lambda x: -x[0])
            return [self.logs[i] for _, i in scores[:top_k]]
