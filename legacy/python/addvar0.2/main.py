from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from fastapi import HTTPException

app = FastAPI(title="addvar")

# In-memory store of logs
LOGS: List[Dict] = []

class LogEntry(BaseModel):
    domain: str = "unknown"
    text: str

class MapRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/logs")
async def add_log(entry: LogEntry):
    LOGS.append({"domain": entry.domain, "text": entry.text})
    return {"status": "ok", "count": len(LOGS)}

# keyword-overlap fallback
def map_query(query: str, logs: List[Dict], top_k: int = 5):
    """Simple keyword-overlap mapper: returns logs sorted by number of shared tokens with query."""
    q_tokens = set([t.lower() for t in query.split() if t.strip()])
    scored = []
    for i, l in enumerate(logs):
        tokens = set([t.lower() for t in l.get("text", "").split() if t.strip()])
        score = len(q_tokens & tokens)
        scored.append((score, i, l))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [item[2] for item in scored[:top_k]]

# Semantic integration (optional)
try:
    from .semantic_integration import build_index, query_index
    SEMANTIC_AVAILABLE = True
except Exception:
    SEMANTIC_AVAILABLE = False

@app.post("/map")
async def map_logs(req: MapRequest):
    if SEMANTIC_AVAILABLE:
        try:
            results = query_index(req.query, req.top_k)
            return {"query": req.query, "results": results}
        except Exception:
            # fallback to keyword overlap if semantic fails
            mapped = map_query(req.query, LOGS, req.top_k)
            return {"query": req.query, "results": mapped}
    else:
        mapped = map_query(req.query, LOGS, req.top_k)
        return {"query": req.query, "results": mapped}

@app.get("/logs")
async def list_logs():
    return {"count": len(LOGS), "logs": LOGS}

@app.post("/build_index")
async def build_semantic_index():
    if not SEMANTIC_AVAILABLE:
        return {"status": "error", "detail": "Semantic modules not available"}
    try:
        build_index(LOGS)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


class ReconcileRequest(BaseModel):
    coherence_vector: List[Dict]
    deltas: Dict


@app.post("/reconcile")
async def reconcile(req: ReconcileRequest):
    try:
        from src.legacy.addvar_adapter import reconcile_adapter
    except Exception:
        raise HTTPException(status_code=500, detail="Legacy adapter not available")
    res = reconcile_adapter(req.coherence_vector, req.deltas)
    if isinstance(res, dict) and res.get('error'):
        raise HTTPException(status_code=500, detail=res['error'])
    return {"status": "ok", "result": res}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.addvar.main:app", host="127.0.0.1", port=8000, reload=True)
