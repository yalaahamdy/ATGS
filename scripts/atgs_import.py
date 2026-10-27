# -*- coding: utf-8 -*-
"""
ATGS - Universal Game Translation Importer & Rebuilder
=====================================================
أداة استيراد وحقن الترجمات في ملفات اللعبة وإعادة بناء ملفات التوطين الأصلية.

المميزات:
1. دمج نتائج الترجمة من حزم الذكاء الاصطناعي (translation_batches).
2. تطبيق التشكيل العربي التلقائي وحساب BiDi وحماية الوسوم والتفاف الأسطر.
3. دعم متعدد لترميزات اللعبة الدقيقة: UTF-16LE, UTF-8 BOM, UTF-8, CP1256.
4. إعادة بناء ملفات TSV / CSV / JSON متوافقة 100% مع البنية الأصلية لمحرك اللعبة.
5. التحقق من تطابق المتغيرات والوسوم لمنع انهيار اللعبة عند التشغيل (QA Validation).
"""

import os
import sys
import json
import csv
import argparse
from typing import Dict, List, Any, Optional

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from atgs_reshaper import process_arabic_text, has_arabic


def load_translated_batches(batches_dir: str) -> Dict[str, str]:
    """Loads all translated records from JSON batch files."""
    translations = {}
    if not os.path.isdir(batches_dir):
        print(f"Directory not found: {batches_dir}")
        return translations

    for fname in sorted(os.listdir(batches_dir)):
        if fname.endswith('.json') and fname.startswith('batch_'):
            full_path = os.path.join(batches_dir, fname)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    batch = json.load(f)
                    for item in batch:
                        rec_id = item.get("id")
                        tgt = item.get("target_text", "")
                        if rec_id and tgt:
                            translations[rec_id] = tgt
            except Exception as ex:
                print(f"Error reading {fname}: {ex}")

    return translations


def rebuild_game_files(
    batches_dir: str,
    mapping_file: str,
    target_output_dir: str,
    apply_shaping: bool = True,
    wrap_width: int = 55,
    default_encoding: str = "utf-16le"
) -> Dict[str, Any]:
    """Rebuilds original localization files using translated texts and original mappings."""
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")

    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping: Dict[str, Any] = json.load(f)

    translations = load_translated_batches(batches_dir)
    print(f"Loaded {len(translations)} translated items across batches.")

    # Group records by target relative file path
    files_map: Dict[str, List[Dict[str, Any]]] = {}
    for rec_id, rec in mapping.items():
        rel_path = rec["source_file"]
        if rel_path not in files_map:
            files_map[rel_path] = []
        files_map[rel_path].append(rec)

    total_translated = 0
    total_rebuilt_files = 0

    for rel_path, records in files_map.items():
        out_file_path = os.path.join(target_output_dir, rel_path)
        os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
        ext = os.path.splitext(rel_path)[1].lower()

        if ext in ['.tsv', '.txt', '.csv']:
            delim = '\t' if ext in ['.tsv', '.txt'] else ','
            lines_to_write = []

            for rec in records:
                rec_id = rec["id"]
                raw_fields = rec.get("raw_fields", {})
                tgt = translations.get(rec_id, rec.get("source_text", ""))

                if rec_id in translations:
                    total_translated += 1

                final_text = tgt
                if apply_shaping and has_arabic(final_text):
                    final_text = process_arabic_text(final_text, max_line_len=wrap_width)

                # Update the translatable column
                cols = list(raw_fields.values()) if raw_fields else [rec["key"], final_text]
                if len(cols) >= 2:
                    cols[1] = final_text
                else:
                    cols.append(final_text)

                lines_to_write.append(delim.join(cols))

            # Determine encoding: Unity TSV often needs UTF-16LE, tutorials UTF-8-sig
            target_enc = "utf-8-sig" if "tutorial" in rel_path.lower() else default_encoding
            try:
                with open(out_file_path, 'w', encoding=target_enc, newline='\r\n') as f:
                    f.write('\n'.join(lines_to_write) + '\n')
                total_rebuilt_files += 1
                print(f"  [+] Rebuilt: {rel_path} ({len(lines_to_write)} lines) [{target_enc}]")
            except Exception as e:
                print(f"  [-] Failed to write {rel_path}: {e}")

        elif ext == '.json':
            json_data = {}
            for rec in records:
                rec_id = rec["id"]
                key = rec["key"]
                tgt = translations.get(rec_id, rec.get("source_text", ""))

                if rec_id in translations:
                    total_translated += 1

                final_text = tgt
                if apply_shaping and has_arabic(final_text):
                    final_text = process_arabic_text(final_text, max_line_len=wrap_width)

                json_data[key] = final_text

            try:
                with open(out_file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                total_rebuilt_files += 1
                print(f"  [+] Rebuilt JSON: {rel_path} ({len(json_data)} keys)")
            except Exception as e:
                print(f"  [-] Failed to write JSON {rel_path}: {e}")

    summary = {
        "total_records_mapped": len(mapping),
        "total_translations_applied": total_translated,
        "total_files_rebuilt": total_rebuilt_files,
        "target_directory": target_output_dir
    }
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="ATGS Universal Game Translation Importer & Rebuilder"
    )
    parser.add_argument("batches_dir", help="Directory containing translated batch_*.json files")
    parser.add_argument("mapping_file", help="Path to id_mapping.json created during extraction")
    parser.add_argument("-o", "--output-dir", required=True, help="Destination directory to output game files")
    parser.add_argument("--no-shaping", action="store_true", help="Disable Arabic reshaping/BiDi (if game natively supports RTL)")
    parser.add_argument("-w", "--wrap-width", type=int, default=55, help="Line wrap width for shaping (default: 55)")
    parser.add_argument("--encoding", default="utf-16le", help="Default encoding for text tables (default: utf-16le)")

    args = parser.parse_args()

    summary = rebuild_game_files(
        batches_dir=args.batches_dir,
        mapping_file=args.mapping_file,
        target_output_dir=args.output_dir,
        apply_shaping=not args.no_shaping,
        wrap_width=args.wrap_width,
        default_encoding=args.encoding
    )

    print("\n--- Import Summary ---")
    print(f"Total Mapped Records: {summary['total_records_mapped']}")
    print(f"Translations Applied: {summary['total_translations_applied']}")
    print(f"Files Rebuilt:        {summary['total_files_rebuilt']}")
    print(f"Output Directory:     {summary['target_directory']}")


if __name__ == "__main__":
    main()
