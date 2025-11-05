# data classes: MemoryNode, Tag, Vector, LedgerEntry
# core/memory/models.py
"""
Neuralexica Core Models
=======================

Defines the basic data structures for the Addvar Memory Engine.
These classes represent atomic memory nodes, tags, and ledger entries.
All other modules (tagging, storage, emotional vectors) will reference these.

Philosophy:
-----------
Memory is not only data retention; it is structural cognition.
These classes are kept minimal to allow iteration on semantics
without reworking persistence or search layers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid


def generate_id() -> str:
    """Return a unique ID string for any memory object."""
    return str(uuid.uuid4())


@dataclass
class Tag:
    """Represents a semantic or symbolic label attached to a MemoryNode."""
    name: str
    confidence: float = 1.0
    meta: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class MemoryNode:
    """
    The atomic unit of Neuralexica memory.

    Attributes
    ----------
    id : unique identifier
    content : textual or symbolic data payload
    tags : semantic / emotional / paralinguistic tags
    vector : optional numeric representation (embedding)
    created_at : creation timestamp
    meta : arbitrary metadata dictionary
    """

    content: str
    tags: List[Tag] = field(default_factory=list)
    vector: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=generate_id)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LedgerEntry:
    """
    Append-only transaction record of system activity.
    Each entry represents an operation performed on memory.
    """

    action: str                  # e.g., 'store', 'recall', 'update', 'merge'
    node_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_node(cls, action: str, node: MemoryNode, **meta):
        """Convenience method for creating an entry directly from a node."""
        return cls(action=action, node_id=node.id, meta=meta)

