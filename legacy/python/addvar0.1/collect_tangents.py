# python
import argparse, os, re, json, csv

TANGENT_ID_RE = re.compile(r'\b(Tangent_[A-Za-z0-9_-]+)\b')
TANGENT_CALL_RE = re.compile(r'\btangent\.(commit|scan|resolve|index)\b', re.IGNORECASE)
TIMESTAMP_RE = re.compile(r'\b(\d{8}T\d{4,6})\b')  # e.g. 20251016T1825 or with seconds

def extract_text_from_json(obj):
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        texts = []
        for v in obj.values():
            texts += extract_text_from_json(v)
        return texts
    if isinstance(obj, list):
        texts = []
        for item in obj:
            texts += extract_text_from_json(item)
        return texts
    return []

def scan_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read()
    except Exception:
        return []
    results = []
    # If looks like JSON, try to parse and extract text nodes
    if path.lower().endswith('.json'):
        try:
            obj = json.loads(raw)
            texts = extract_text_from_json(obj)
            full_text = "\n".join(texts)
        except Exception:
            full_text = raw
    else:
        full_text = raw

    # find tangent ids and calls
    for m in TANGENT_ID_RE.finditer(full_text):
        start = max(0, m.start() - 120)
        snippet = full_text[start:m.end() + 120].replace('\n', ' ')
        ts_match = TIMESTAMP_RE.search(snippet)
        results.append({
            'file': path,
            'type': 'id',
            'id': m.group(1),
            'timestamp': ts_match.group(1) if ts_match else '',
            'snippet': snippet.strip()
        })
    for m in TANGENT_CALL_RE.finditer(full_text):
        start = max(0, m.start() - 120)
        snippet = full_text[start:m.end() + 120].replace('\n', ' ')
        ts_match = TIMESTAMP_RE.search(snippet)
        results.append({
            'file': path,
            'type': 'call',
            'id': m.group(0),
            'timestamp': ts_match.group(1) if ts_match else '',
            'snippet': snippet.strip()
        })
    # also try to capture tabular rows that mention Tangent_ (common in your md)
    table_row_re = re.compile(r'^\|.*Tangent_[A-Za-z0-9_-]+.*$', re.MULTILINE)
    for m in table_row_re.finditer(full_text):
        row = m.group(0).replace('\n', ' ')
        tid = TANGENT_ID_RE.search(row)
        results.append({
            'file': path,
            'type': 'table_row',
            'id': tid.group(1) if tid else '',
            'timestamp': TIMESTAMP_RE.search(row).group(1) if TIMESTAMP_RE.search(row) else '',
            'snippet': row.strip()
        })
    return results

def walk_and_collect(root):
    collected = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(('.json', '.md', '.txt', '.html', '.htm')):
                collected += scan_file(os.path.join(dirpath, fn))
    return collected

def write_csv(rows, out):
    keys = ['file', 'type', 'id', 'timestamp', 'snippet']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in keys})

def write_json(path, rows):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write JSON: {e}")

def main():
    p = argparse.ArgumentParser(description='Collect tangent entries across exported chat files.')
    p.add_argument('root', help='folder with exports or chat files')
    p.add_argument('--out', default='tangents.csv', help='CSV output path')
    p.add_argument('--out-json', default='tangents.json', help='JSON output path')
    args = p.parse_args()
    rows = walk_and_collect(args.root)
    write_csv(rows, args.out)
    write_json(args.out_json, rows)
    print(f'Found {len(rows)} candidate tangents. Written CSV to {args.out} and JSON to {args.out_json}')

if __name__ == '__main__':
    main()

# Example usage Change to the folder containing the script
#cd "C:\Users\Justin\My Drive\Ledgar\python scripts"
# Run against your exported chat folder and write output somewhere
#python collect_tangents.py "C:\Users\Justin\My Drive\Ledgar\exports\chatgpt-export" --out "C:\Users\Justin\My Drive\Ledgar\outputs\tangents.csv"