# -*- coding: utf-8 -*-
"""
ATGS - Arabic Translate Game Skill Unified CLI
==============================================
واجهة سطر الأوامر الموحدة لجميع أدوات تعريب ألعاب الفيديو.
"""

import sys
import os
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from atgs_reshaper import process_arabic_text
from atgs_extract import extract_from_file, build_batches
from atgs_import import rebuild_game_files
from merge_to_font_atlas import merge_font


def main():
    parser = argparse.ArgumentParser(
        prog="atgs",
        description="ATGS (Arabic Translate Game Skill) - Universal Game Localization Suite"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: reshape
    p_reshape = subparsers.add_parser("reshape", help="Reshape Arabic text and compute visual BiDi for game engines")
    p_reshape.add_argument("text", nargs="?", help="Arabic text string")
    p_reshape.add_argument("-i", "--input-file", help="Input file (txt/json)")
    p_reshape.add_argument("-o", "--output-file", help="Output file")
    p_reshape.add_argument("-w", "--wrap-width", type=int, default=55, help="Line wrap width (default: 55)")
    p_reshape.add_argument("--force-rtl", action="store_true", help="Force BiDi reversal")

    # Command: extract
    p_extract = subparsers.add_parser("extract", help="Extract translatable game files into structured batches")
    p_extract.add_argument("source_dir", help="Directory containing game localization files")
    p_extract.add_argument("-o", "--output-dir", default="./atgs_extracted", help="Destination batches directory")
    p_extract.add_argument("-b", "--batch-size", type=int, default=150, help="Records per translation batch")
    p_extract.add_argument("-e", "--extensions", default="tsv,txt,csv,json", help="Comma-separated extensions")

    # Command: import
    p_import = subparsers.add_parser("import", help="Import translated batches back into game files")
    p_import.add_argument("batches_dir", help="Directory of translated batch_*.json files")
    p_import.add_argument("mapping_file", help="Path to id_mapping.json")
    p_import.add_argument("-o", "--output-dir", required=True, help="Destination directory for game files")
    p_import.add_argument("-w", "--wrap-width", type=int, default=55, help="Line wrap width for shaping (default: 55)")
    p_import.add_argument("--no-shaping", action="store_true", help="Disable Arabic reshaping/BiDi")
    p_import.add_argument("--encoding", default="utf-16le", help="Default file encoding (default: utf-16le)")

    # Command: pixel-merge
    p_pixel = subparsers.add_parser("pixel-merge", help="Merge 1:1 pixel art Arabic font strip into font atlas")
    p_pixel.add_argument("atlas_png", help="Path to game font atlas PNG")
    p_pixel.add_argument("-o", "--output-png", help="Path to output merged PNG")
    p_pixel.add_argument("--v-offset", type=int, default=210, help="Vertical offset in atlas (default: 210)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "reshape":
        if args.text:
            print(process_arabic_text(args.text, max_line_len=args.wrap_width, force_rtl=args.force_rtl))
        elif args.input_file:
            from atgs_reshaper import main as reshaper_main
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            reshaper_main()
        else:
            p_reshape.print_help()

    elif args.command == "extract":
        allowed_exts = set('.' + ext.strip().lower().lstrip('.') for ext in args.extensions.split(','))
        all_records = []
        for root, _, files in os.walk(args.source_dir):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in allowed_exts:
                    full = os.path.join(root, f)
                    try:
                        recs = extract_from_file(full, args.source_dir)
                        if recs:
                            all_records.extend(recs)
                    except Exception as e:
                        print(f"Error reading {f}: {e}")
        if all_records:
            summary = build_batches(all_records, args.output_dir, batch_size=args.batch_size)
            print(f"Successfully extracted {len(all_records)} records into {summary['batch_count']} batches.")
        else:
            print("No records extracted.")

    elif args.command == "import":
        summary = rebuild_game_files(
            batches_dir=args.batches_dir,
            mapping_file=args.mapping_file,
            target_output_dir=args.output_dir,
            apply_shaping=not args.no_shaping,
            wrap_width=args.wrap_width,
            default_encoding=args.encoding
        )
        print(f"Rebuild completed: {summary['total_files_rebuilt']} files generated.")

    elif args.command == "pixel-merge":
        merge_font(args.atlas_png, args.output_png, v_offset=args.v_offset)


if __name__ == "__main__":
    main()
