# python
import os
import re
import json
import csv
import argparse
from collections import defaultdict, Counter
from datetime import datetime

TANGENT_ID_RE = re.compile(r'\b(Tangent_[A-Za-z0-9_-]+)\b')
TANGENT_CALL_RE = re.compile(r'\btangent\.(commit|scan|resolve|index)\b', re.IGNORECASE)
TIMESTAMP_RE = re.compile(r'\b(\d{8}T\d{4,6})\b')  # e.g. 20251016T1825 or with seconds

FIRST_PERSON = re.compile(r'\b(I|me|my|mine|we|our|us)\b', re.I)
SPEAKER_LABEL = re.compile(r'^\s*([A-Za-z0-9 _@.-]{1,40}):\s*', re.M)

def load_file_text(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return ''

def extract_text_from_json(obj):
    """
    Recursively find message-like dicts in JSON exports.
    Returns list of dicts: {'speaker': label_or_role, 'text': content, 'timestamp': maybe}
    """
    out = []
    if isinstance(obj, dict):
        # common forms: {'role': 'user', 'content': '...'} or {'author': {'role':'user'}, 'content': {'text':'...'}}
        if ('role' in obj and ('content' in obj or 'text' in obj)) or ('author' in obj and 'content' in obj):
            speaker = obj.get('role') or (obj.get('author') and (obj['author'].get('role') if isinstance(obj['author'], dict) else str(obj['author'])))
            # try a few keys for text
            text = ''
            if isinstance(obj.get('content'), str):
                text = obj['content']
            elif isinstance(obj.get('content'), dict):
                # often {'content': {'text': '...'}} or {'content': {'parts': [... ]}}
                if 'text' in obj['content']:
                    text = obj['content']['text']
                elif 'parts' in obj['content'] and isinstance(obj['content']['parts'], list):
                    text = '\n'.join([p for p in obj['content']['parts'] if isinstance(p, str)])
            elif 'message' in obj:
                text = obj['message']
            elif 'text' in obj:
                text = obj['text']
            ts = obj.get('created') or obj.get('timestamp') or obj.get('date')
            out.append({'speaker': str(speaker) if speaker is not None else None, 'text': str(text or ''), 'timestamp': str(ts or '')})
        else:
            for v in obj.values():
                out.extend(extract_text_from_json(v))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(extract_text_from_json(item))
    return out

def parse_plain_text_messages(text):
    """
    Turn plain text/markdown transcripts into message blocks.
    Heuristics:
      - lines starting with 'Name:' are speaker-labeled.
      - otherwise split on blank lines and assume alternation (user first).
    Returns list of {'speaker': label_or_None, 'text': text, 'timestamp': maybe}
    """
    messages = []
    # if many 'Label:' lines, use that
    labels = list(SPEAKER_LABEL.finditer(text))
    if labels:
        # split by label matches
        parts = SPEAKER_LABEL.split(text)
        # split returns [prefix, label1, body1, label2, body2, ...] if leading prefix present
        it = iter(parts)
        prefix = next(it, '')
        while True:
            try:
                label = next(it)
                body = next(it)
                messages.append({'speaker': label.strip(), 'text': body.strip(), 'timestamp': ''})
            except StopIteration:
                break
        if not messages and prefix.strip():
            messages.append({'speaker': None, 'text': prefix.strip(), 'timestamp': ''})
        return messages

    # else split on double newlines and assume alternating speakers
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
    if not blocks:
        return []
    # check if each block starts with a timestamp - pull it out
    for b in blocks:
        ts_m = TIMESTAMP_RE.search(b)
        ts = ts_m.group(1) if ts_m else ''
        messages.append({'speaker': None, 'text': b, 'timestamp': ts})
    # if speaker unknown, caller will infer using heuristics
    return messages

def infer_user_label(messages):
    """
    If messages contain explicit role labels like 'user' or 'assistant', map them.
    Otherwise, choose the speaker label that uses first-person pronouns most as 'user'.
    If no labels, assume alternating and that the first block is the user.
    Returns (user_label, assistant_label, labeled_messages_list)
    labeled_messages_list: same as messages but with 'speaker' filled ('user'/'assistant' or specific label)
    """
    # copy to avoid mutating original
    labeled = [dict(m) for m in messages]

    # if any message has role-like label
    distinct = Counter([m['speaker'] for m in labeled if m['speaker']])
    # normalize known roles
    for k in list(distinct):
        nk = None
        if isinstance(k, str) and k.lower() in ('user', 'me', 'human', 'you', 'person', 'client'):
            nk = 'user'
        if isinstance(k, str) and k.lower() in ('assistant', 'ai', 'gpt', 'bot', 'system'):
            nk = 'assistant'
        if nk:
            for m in labeled:
                if m['speaker'] == k:
                    m['speaker'] = nk
    # if we now have messages labeled 'user'/'assistant', done
    has_user = any(m['speaker'] == 'user' for m in labeled)
    has_assistant = any(m['speaker'] == 'assistant' for m in labeled)
    if has_user or has_assistant:
        # assign any remaining unlabeled by alternating fill
        last = None
        for m in labeled:
            if m['speaker'] in ('user', 'assistant'):
                last = m['speaker']
            else:
                # assign opposite of last if last known, else assign 'user' for first unknown
                if last is None:
                    m['speaker'] = 'user'
                    last = 'user'
                else:
                    m['speaker'] = 'assistant' if last == 'user' else 'user'
                    last = m['speaker']
        return 'user', 'assistant', labeled

    # otherwise, group by label strings (if multiple different labels present)
    label_texts = defaultdict(list)
    for m in labeled:
        key = m['speaker'] if m['speaker'] else '__anon__'
        label_texts[key].append(m['text'])

    # if multiple named speakers, compute first-person usage
    scores = {}
    for label, texts in label_texts.items():
        combined = '\n'.join(texts)
        scores[label] = len(FIRST_PERSON.findall(combined))
    # choose label with highest first-person as user
    user_label = max(scores.items(), key=lambda kv: kv[1])[0]
    # if anonymous-only, assume alternating user-first
    if user_label == '__anon__' and len(labeled) > 0:
        for i, m in enumerate(labeled):
            m['speaker'] = 'user' if i % 2 == 0 else 'assistant'
        return 'user', 'assistant', labeled

    # map labels: user_label -> 'user', others -> 'assistant' (if many speakers, they