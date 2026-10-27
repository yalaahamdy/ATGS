# -*- coding: utf-8 -*-
"""
ATGS - Run Example
يوضح هذا المثال كيفية استخدام مكتبة ATGS لمعالجة نصوص لعبة كاملة وتجهيزها للعرض في محركات LTR.
"""

import os
import sys
import json

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from atgs_reshaper import process_arabic_text

def run():
    sample_file = os.path.join(os.path.dirname(__file__), 'sample_game_strings_ar.json')
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=== نصوص الإدخال الأصلية ===")
    for k, v in data.items():
        print(f"{k}: {v}")

    print("\n=== النصوص بعد معالجة ATGS (جاهزة لمحرك اللعبة) ===")
    processed = {}
    for k, v in data.items():
        shaped = process_arabic_text(v, max_line_len=45)
        processed[k] = shaped
        print(f"{k}:\n  {shaped}")

    out_file = os.path.join(os.path.dirname(__file__), 'sample_game_strings_shaped.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    print(f"\nتم حفظ النتيجة المعالجة في: {out_file}")

if __name__ == "__main__":
    run()
