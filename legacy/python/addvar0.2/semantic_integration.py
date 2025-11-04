from .semantic import SemanticIndex

# Simple integration helpers
_index = None

def build_index(logs):
    global _index
    si = SemanticIndex(logs)
    si.build()
    _index = si


def query_index(query, top_k=5):
    if _index is None:
        raise RuntimeError("Index not built")
    return _index.query(query, top_k)
