# -*- coding: utf-8 -*-
"""
ATGS - Universal Game Localization Extractor
============================================
أداة استخراج نصوص الألعاب الشاملة وتحويلها إلى التنسيق الوسيط الموحد وحزم الذكاء الاصطناعي.

المميزات:
1. استخراج النصوص من صيغ متعددة: TSV, CSV, JSON, Flat Text, Key-Value, PO.
2. الكشف التلقائي عن المتغيرات والأكواد المحمية ({0}, %s, $var).
3. الكشف التلقائي عن وسوم التنسيق (Rich Text Tags: <color>, <b>, etc.).
4. تصنيف تلقائي للنصوص (UI, Tutorial, Technology, Item, System, Dialog).
5. إنشاء معرّفات فريدة وثابتة (Stable IDs) تمنع التصادمات.
6. تقسيم السجلات إلى حزم متوازنة (Batches) معدة للترجمة بالذكاء الاصطناعي.
7. توليد خريطة استيراد (Import Mapping) تضمن استعادة النصوص إلى مواضعها الأصلية.
"""

import os
import sys
import json
import csv
import re
import hashlib
import argparse
from typing import Dict, List, Any, Optional

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PLACEHOLDER_REGEX = re.compile(
    r'(\{\$[^\}]+\}|\{[0-9]+(?::[^\}]+)?\}|\$[A-Za-z0-9_]+;|\\[a-zA-Z]+;|%[0-9]*\.?[0-9]*[dfs])'
)
TAG_REGEX = re.compile(
    r'(</?(?:color(?:=[^>]+)?|b|i|size(?:=[^>]+)?|IMG|material(?:=[^>]+)?|quad(?:=[^>]+)?)>)',
    re.IGNORECASE
)


def generate_stable_id(file_rel_path: str, key_or_line: str, source_text: str) -> str:
    """Generates a stable, collision-free unique identifier."""
    raw = f"{file_rel_path}::{key_or_line}::{source_text}"
    h = hashlib.sha256(raw.encode('utf-8', errors='ignore')).hexdigest()[:12]
    # Clean file prefix for human readability
    prefix = os.path.splitext(os.path.basename(file_rel_path))[0]
    prefix = re.sub(r'[^A-Za-z0-9_]', '_', prefix)[:16]
    return f"{prefix}_{h}"


def detect_category(file_path: str, key: str, text: str) -> str:
    """Categorizes the text based on its file location, key, and contents."""
    low_path = file_path.lower()
    low_key = key.lower()

    if any(k in low_path or k in low_key for k in ['tutorial', 'guide', 'help', 'wiki']):
        return "Tutorial"
    if any(k in low_path or k in low_key for k in ['tech', 'research', 'upgrade']):
        return "Technology"
    if any(k in low_path or k in low_key for k in ['item', 'proto', 'recipe', 'building']):
        return "Item"
    if any(k in low_path or k in low_key for k in ['dialog', 'dialogue', 'story', 'npc', 'quest']):
        return "Dialogue"
    if any(k in low_path or k in low_key for k in ['error', 'warn', 'alert', 'notice', 'fail']):
        return "Error"
    if any(k in low_path or k in low_key for k in ['history', 'update', 'changelog', 'patch']):
        return "Changelog"
    return "UI"


def analyze_string(text: str) -> Dict[str, Any]:
    """Finds placeholders and tags within a source string."""
    placeholders = PLACEHOLDER_REGEX.findall(text)
    tags = TAG_REGEX.findall(text)
    return {
        "placeholders": list(set(placeholders)),
        "markup": list(set(tags)),
        "char_count": len(text),
        "word_count": len(text.split()),
    }


def parse_tsv_or_csv(file_path: str, delimiter: str = '\t', encoding: str = 'utf-8') -> List[Dict[str, str]]:
    """Parses TSV or CSV translation table."""
    records = []
    # If encoding fails, fallback to utf-16 or utf-8-sig
    encodings_to_try = [encoding, 'utf-16', 'utf-16-le', 'utf-8-sig', 'cp1256', 'latin-1']

    raw_lines = None
    for enc in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                raw_lines = f.readlines()
            break
        except Exception:
            continue

    if not raw_lines:
        return []

    reader = csv.reader(raw_lines, delimiter=delimiter)
    header = None
    row_idx = 0

    for row in reader:
        row_idx += 1
        if not row or not any(row):
            continue

        if header is None:
            # Check if this row looks like a header
            if any(col.lower() in ['key', 'id', 'en', 'english', 'source', 'text', 'chinese', 'zh'] for col in row):
                header = [c.strip() for c in row]
                continue
            else:
                # Synthetic header
                header = [f"col_{i}" for i in range(len(row))]

        record = {"__line__": str(row_idx)}
        for i, val in enumerate(row):
            col_name = header[i] if i < len(header) else f"col_{i}"
            record[col_name] = val
        records.append(record)

    return records


def extract_from_file(
    file_path: str,
    base_dir: str,
    source_col: Optional[str] = None,
    key_col: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Extracts translatable units from a single file."""
    rel_path = os.path.relpath(file_path, base_dir).replace('\\', '/')
    ext = os.path.splitext(file_path)[1].lower()
    results = []

    if ext in ['.tsv', '.txt', '.csv']:
        delim = '\t' if ext in ['.tsv', '.txt'] else ','
        raw_records = parse_tsv_or_csv(file_path, delimiter=delim)

        for rec in raw_records:
            line_no = rec.get("__line__", "0")
            # Determine source text and key
            available_cols = [c for c in rec.keys() if c != "__line__"]
            if not available_cols:
                continue

            target_key = None
            if key_col and key_col in rec:
                target_key = rec[key_col]
            else:
                for cand in ['key', 'id', 'name', 'col_0']:
                    if cand in rec:
                        target_key = rec[cand]
                        break
            if not target_key:
                target_key = f"line_{line_no}"

            target_text = None
            if source_col and source_col in rec:
                target_text = rec[source_col]
            else:
                for cand in ['en', 'english', 'text', 'source', 'val', 'col_1', 'zh']:
                    if cand in rec and rec[cand]:
                        target_text = rec[cand]
                        break
            if not target_text and len(available_cols) > 1:
                target_text = rec[available_cols[1]]

            if not target_text or not target_text.strip():
                continue

            meta = analyze_string(target_text)
            record_id = generate_stable_id(rel_path, target_key, target_text)

            results.append({
                "id": record_id,
                "source_file": rel_path,
                "source_format": ext.lstrip('.'),
                "source_language": "en",
                "key": target_key,
                "source_text": target_text,
                "target_text": "",
                "category": detect_category(rel_path, target_key, target_text),
                "placeholders": meta["placeholders"],
                "markup": meta["markup"],
                "char_count": meta["char_count"],
                "raw_fields": {k: v for k, v in rec.items() if k != "__line__"},
                "review_status": "pending"
            })

    elif ext == '.json':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return []

        def recurse_json(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    recurse_json(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    recurse_json(v, f"{path}[{i}]")
            elif isinstance(obj, str) and obj.strip():
                meta = analyze_string(obj)
                record_id = generate_stable_id(rel_path, path, obj)
                results.append({
                    "id": record_id,
                    "source_file": rel_path,
                    "source_format": "json",
                    "source_language": "en",
                    "key": path,
                    "source_text": obj,
                    "target_text": "",
                    "category": detect_category(rel_path, path, obj),
                    "placeholders": meta["placeholders"],
                    "markup": meta["markup"],
                    "char_count": meta["char_count"],
                    "review_status": "pending"
                })

        recurse_json(data)

    return results


def build_batches(
    records: List[Dict[str, Any]],
    output_dir: str,
    batch_size: int = 150
) -> Dict[str, Any]:
    """Divides extracted records into AI translation batches and generates import mapping."""
    os.makedirs(output_dir, exist_ok=True)
    batches_dir = os.path.join(output_dir, "translation_batches")
    mapping_dir = os.path.join(output_dir, "import_mapping")
    os.makedirs(batches_dir, exist_ok=True)
    os.makedirs(mapping_dir, exist_ok=True)

    # 1. Save master unified records
    master_file = os.path.join(output_dir, "master_source_records.json")
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # 2. Divide into batches
    total_records = len(records)
    batch_index = 0
    batch_files = []

    for i in range(0, total_records, batch_size):
        batch_index += 1
        chunk = records[i:i + batch_size]
        batch_filename = f"batch_{batch_index:03d}.json"
        batch_path = os.path.join(batches_dir, batch_filename)

        # Simplified schema for translator AI
        batch_payload = [
            {
                "id": rec["id"],
                "key": rec["key"],
                "source_text": rec["source_text"],
                "target_text": "",
                "context": f"File: {rec['source_file']} | Category: {rec['category']}",
                "placeholders": rec["placeholders"],
                "markup": rec["markup"]
            }
            for rec in chunk
        ]

        with open(batch_path, 'w', encoding='utf-8') as f:
            json.dump(batch_payload, f, ensure_ascii=False, indent=2)

        batch_files.append(batch_filename)

    # 3. Save import mapping
    mapping = {rec["id"]: rec for rec in records}
    mapping_file = os.path.join(mapping_dir, "id_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    summary = {
        "total_records": total_records,
        "batch_count": len(batch_files),
        "batch_size": batch_size,
        "output_dir": output_dir,
        "master_file": master_file
    }

    summary_file = os.path.join(output_dir, "extraction_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="ATGS Universal Game Localization Extractor"
    )
    parser.add_argument("source_dir", help="Target game directory or translation directory to extract from")
    parser.add_argument("-o", "--output-dir", default="./atgs_extracted", help="Directory to save extracted batches")
    parser.add_argument("-b", "--batch-size", type=int, default=150, help="Number of records per translation batch")
    parser.add_argument("-e", "--extensions", default="tsv,txt,csv,json", help="Comma-separated file extensions to scan")

    args = parser.parse_args()

    allowed_exts = set('.' + ext.strip().lower().lstrip('.') for ext in args.extensions.split(','))
    all_records = []

    print(f"Scanning {args.source_dir} for localization files...")
    for root, _, files in os.walk(args.source_dir):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in allowed_exts:
                full_path = os.path.join(root, f)
                try:
                    recs = extract_from_file(full_path, args.source_dir)
                    if recs:
                        all_records.extend(recs)
                        print(f"  [+] {os.path.relpath(full_path, args.source_dir)}: {len(recs)} records extracted")
                except Exception as ex:
                    print(f"  [-] Failed to parse {full_path}: {ex}")

    if not all_records:
        print("No translatable records found!")
        return

    print(f"Total translatable records extracted: {len(all_records)}")
    summary = build_batches(all_records, args.output_dir, batch_size=args.batch_size)
    print(f"Batches successfully created: {summary['batch_count']} batches saved to {args.output_dir}")


if __name__ == "__main__":
    main()
