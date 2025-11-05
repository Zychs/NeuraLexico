# Memory Module — Addvar Core Engine

> The memory module serves as the very substrate of the entire system; it must be versatile and compatible.

---

## Purpose
The memory engine provides the foundational substrate for all Neuralexica processes.  
Every interaction, semantic object, or emotional vector eventually resolves into a **memory node**—an atomic record that can be recalled, compared, merged, or symbolically reasoned over.

This module is designed to be **agnostic of interface and modality**:  
it should support text, audio, and future paralinguistic data streams without re-architecture.

---

## Architectural Intent
Memory is treated as a **ledger + graph hybrid**:

- **Ledger layer** — ensures chronological, append-only integrity.  
  Each event (journal entry, transcript, extracted vector) is a verifiable addition.  
- **Graph layer** — provides semantic relationships, similarity search, and cross-context linking.

Together they form an adaptive substrate where cognition emerges from traceable interactions.

---

## Core Components
| File | Role |
|------|------|
| `engine.py` | Orchestrates memory operations: store, recall, merge, tag. |
| `models.py` | Defines data models (`MemoryNode`, `Tag`, `LedgerEntry`). |
| `storage/json_store.py` | Local prototype persistence for lightweight testing. |
| `storage/vector_store.py` | Stub for high-dimensional vector search (FAISS/Chroma). |
| `utils.py` | Common utilities: hashing, timestamps, normalization. |

---

## Design Requirements
- Must persist data across sessions without loss of relational structure.  
- Must be compatible with **semantic and emotional indexing layers**.  
- Must expose a **minimal, stable API** to higher systems (`/interface` modules).  
- Should allow experimentation with multiple storage backends (JSON → SQLite → Vector DB).  
- Should prioritize transparency and introspection over opacity.

---

## Current Status
✅ Initial scaffold committed  
🔧 Defining data classes and I/O behavior  
⏳ Next milestone: implement `MemoryNode` and test `JsonStore.save()`  

---

## Notes
The memory module is not a database—it is a **thinking substrate**.  
Its evolution should be guided by clarity, not complexity:  
each new feature must answer the question, *“Does this make memory more alive or more opaque?”*
