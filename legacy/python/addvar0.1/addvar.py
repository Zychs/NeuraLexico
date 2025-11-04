import json
from datetime import datetime

def reconcile(coherence_vector, deltas):
    """
    Minimal reconcile() for development.
    Returns a summary dict and writes reconciliation_result.json nearby.
    """
    summary = {
        'generated_at': datetime.utcnow().strftime("%Y%m%dT%H%M%S"),
        'top_ids': [item['id'] for item in coherence_vector],
        'counts': {
            'top': len(coherence_vector),
            'added': len(deltas.get('added', [])),
            'removed': len(deltas.get('removed', [])),
            'changed': len(deltas.get('changed', []))
        }
    }
    try:
        with open('reconciliation_result.json', 'w', encoding='utf-8') as f:
            json.dump({'summary': summary, 'deltas': deltas, 'coherence_vector': coherence_vector}, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return summary