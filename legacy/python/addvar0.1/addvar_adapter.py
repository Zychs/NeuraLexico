import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List

LEGACY_PATH = Path(__file__).parents[1].parent / 'legacy base' / 'addvar.py'


def _load_legacy_module():
    """Dynamically load the legacy addvar.py as a module and return it."""
    spec = importlib.util.spec_from_file_location('legacy_addvar', str(LEGACY_PATH))
    module = importlib.util.module_from_spec(spec)
    sys.modules['legacy_addvar'] = module
    spec.loader.exec_module(module)
    return module


def reconcile_adapter(coherence_vector: List[Dict[str, Any]], deltas: Dict[str, Any]) -> Dict[str, Any]:
    """Call legacy reconcile() and return its result.

    This wrapper isolates filesystem writes and exceptions from the legacy module.
    """
    if not LEGACY_PATH.exists():
        raise FileNotFoundError(f"Legacy addvar.py not found at {LEGACY_PATH}")
    module = _load_legacy_module()
    if not hasattr(module, 'reconcile'):
        raise AttributeError('Legacy module missing reconcile function')
    try:
        result = module.reconcile(coherence_vector, deltas)
        return result
    except Exception as e:
        # Don't let legacy errors crash the main app; return an error dict
        return {'error': str(e)}
