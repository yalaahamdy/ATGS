# -*- coding: utf-8 -*-
"""
ATGS - Arabic Reshaper & BiDi Processing Engine for Games
=========================================================
محرك تشكيل النصوص العربية ومعالجة الاتجاه ثنائي الاتجاه (BiDi) المخصص للألعاب.

المميزات:
1. التشكيل العربي الكامل إلى أشكال اليونيكود (Presentation Forms-B / Forms-A).
2. معالجة BiDi وتوجيه النصوص LTR لمحركات الألعاب التي تفتقر لدعم RTL الأصلي (مثل Unity Legacy uGUI).
3. حماية تامة لوسوم التنسيق (Rich Text Tags: <color>, <b>, <i>, <size>, etc.).
4. حماية تامة للمتغيرات والأكواد ({0}, {$var}, $LKEY;, %s, %d, etc.).
5. التفاف الأسطر الذكي متوافق الوسوم (Tag-safe Multiline Word-Wrapping) لمنع انقلاب الأسطر في uGUI.
6. تنظيف حركات الإعراب المتراكبة (Harakat stripping) لتفادي الفجوات البصرية وتفكك الحروف في خطوط الألعاب.
7. تصحيح اتجاه الأقواس وعلامات الترقيم في السياق العربي.
"""

import sys
import re
import argparse
import json
from typing import List, Optional

# Ensure standard UTF-8 console output
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    raise ImportError(
        "Missing dependencies! Please run: pip install arabic-reshaper python-bidi"
    )

# Regular expressions for Arabic detection and token protection
ARABIC_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')

# Protected atomic tokens (variables, engine keywords, format specifiers)
PROTECTED_TOKEN_RE = re.compile(
    r'(\{\$[^\}]+\}|\{[0-9]+(?::[^\}]+)?\}|\$[A-Za-z0-9_]+;|\\[a-zA-Z]+;|%[0-9]*\.?[0-9]*[dfs])'
)

# Unity & Game Engines Rich Text tags (e.g. <color=#FF0000>, <b>, </b>, <size=20>, etc.)
TAG_TOKEN_RE = re.compile(
    r'(</?(?:color(?:=[^>]+)?|b|i|size(?:=[^>]+)?|IMG|material(?:=[^>]+)?|quad(?:=[^>]+)?)>)',
    re.IGNORECASE
)

# Standard reshaper instance configured for game engines
DEFAULT_RESHAPER_CONFIG = {
    'delete_harakat': True,
    'delete_tatweel': False,
    'support_ligatures': True,
}
_default_reshaper = arabic_reshaper.ArabicReshaper(configuration=DEFAULT_RESHAPER_CONFIG)


def has_arabic(text: str) -> bool:
    """Returns True if the string contains any Arabic characters."""
    return bool(text and ARABIC_RE.search(text))


def strip_markup_for_len(text: str) -> int:
    """Returns the visible character length of text excluding tags and protected tokens."""
    no_tags = TAG_TOKEN_RE.sub('', text)
    no_tokens = PROTECTED_TOKEN_RE.sub('X', no_tags)
    return len(no_tokens)


def wrap_text_tag_safe(text: str, max_chars: int = 55) -> List[str]:
    """
    Splits long multiline text into visual lines safely without breaking Rich Text tags
    or protected variables. Crucial for Unity uGUI where reversing multiline text
    directly flips line orders bottom-to-top.
    """
    if strip_markup_for_len(text) <= max_chars:
        return [text]

    words = text.split(' ')
    lines = []
    cur_line = []
    cur_len = 0

    for w in words:
        w_len = strip_markup_for_len(w)
        if cur_line and (cur_len + 1 + w_len > max_chars):
            lines.append(' '.join(cur_line))
            cur_line = [w]
            cur_len = w_len
        else:
            cur_line.append(w)
            cur_len += (1 if cur_line else 0) + w_len

    if cur_line:
        lines.append(' '.join(cur_line))

    return lines


def shape_and_bidi_plain(text: str, force_rtl: bool = False, reshaper_instance=None) -> str:
    """
    Applies Arabic reshaping and computes the visual string for LTR rendering engines.
    Safely preserves protected tokens and handles brackets.
    """
    if not text:
        return text
    if not force_rtl and not has_arabic(text):
        return text

    active_reshaper = reshaper_instance or _default_reshaper

    saved_tokens = []

    def save_tok(m):
        idx = len(saved_tokens)
        saved_tokens.append(m.group(0))
        alpha_id = ""
        n = idx
        for _ in range(4):
            alpha_id += chr(ord('A') + (n % 26))
            n //= 26
        return f"ZXQ{alpha_id}QXZ"

    temp = PROTECTED_TOKEN_RE.sub(save_tok, text)
    shaped = active_reshaper.reshape(temp) if has_arabic(temp) else temp
    visual = get_display(shaped, base_dir='R')

    # Restore protected tokens
    for idx, orig in enumerate(saved_tokens):
        alpha_id = ""
        n = idx
        for _ in range(4):
            alpha_id += chr(ord('A') + (n % 26))
            n //= 26
        visual = visual.replace(f"ZXQ{alpha_id}QXZ", orig)

    return visual


def shape_and_bidi_line(line: str, force_rtl: bool = False, reshaper_instance=None) -> str:
    """
    Shapes and reverses a single line containing possible Rich Text tags (<color>, <b>, etc.).
    Preserves tag placement and direction while transforming Arabic content between tags.
    """
    if not line:
        return line

    has_ar = has_arabic(line)
    if not force_rtl and not has_ar:
        return line

    is_line_arabic = has_ar or force_rtl
    tokens = TAG_TOKEN_RE.split(line)
    processed = []

    for tok in tokens:
        if not tok:
            continue
        if TAG_TOKEN_RE.match(tok):
            # Rich text tag: preserve as-is without flipping
            processed.append(tok)
        else:
            processed.append(shape_and_bidi_plain(tok, force_rtl=is_line_arabic, reshaper_instance=reshaper_instance))

    if is_line_arabic:
        # Reverse tag order so that in visual LTR rendering, outer tags wrap correctly
        processed.reverse()

    return ''.join(processed)


def process_arabic_text(
    text: str,
    max_line_len: int = 55,
    force_rtl: bool = False,
    delete_harakat: bool = True
) -> str:
    """
    Main entry point for processing a full text string for game engines.
    Handles explicit newlines, multiline wrapping, and rich text formatting.

    Args:
        text: The source Arabic or mixed text.
        max_line_len: Maximum visible line width before word-wrapping (set 0 to disable wrapping).
        force_rtl: Force BiDi reversal even if text has no Arabic letters.
        delete_harakat: Strip combining diacritics to avoid gaps in fixed/pixel fonts.

    Returns:
        Visual string ready for LTR text renderers.
    """
    if not text:
        return text

    if not force_rtl and not has_arabic(text):
        return text

    # Handle reshaper configuration
    cfg = {
        'delete_harakat': delete_harakat,
        'delete_tatweel': False,
        'support_ligatures': True,
    }
    custom_reshaper = arabic_reshaper.ArabicReshaper(configuration=cfg)

    # Check for escaped newlines or literal newlines
    has_escaped_nl = r'\n' in text and '\n' not in text
    split_char = r'\n' if has_escaped_nl else '\n'

    paragraphs = text.split(split_char)
    processed_paragraphs = []

    for para in paragraphs:
        if not para:
            processed_paragraphs.append("")
            continue

        if max_line_len > 0 and strip_markup_for_len(para) > max_line_len:
            wrapped_lines = wrap_text_tag_safe(para, max_chars=max_line_len)
        else:
            wrapped_lines = [para]

        shaped_lines = [
            shape_and_bidi_line(l, force_rtl=force_rtl, reshaper_instance=custom_reshaper)
            for l in wrapped_lines
        ]
        processed_paragraphs.append(split_char.join(shaped_lines))

    return split_char.join(processed_paragraphs)


# Command Line Interface
def main():
    parser = argparse.ArgumentParser(
        description="ATGS Arabic Reshaper & BiDi Processing Tool for Games"
    )
    parser.add_argument("text", nargs="?", help="Text string to process")
    parser.add_argument("-i", "--input-file", help="Input text or JSON file")
    parser.add_argument("-o", "--output-file", help="Output text or JSON file")
    parser.add_argument("-w", "--wrap-width", type=int, default=55, help="Line wrap width (default: 55, 0 to disable)")
    parser.add_argument("--keep-harakat", action="store_true", help="Keep combining diacritics")
    parser.add_argument("--force-rtl", action="store_true", help="Force RTL processing")

    args = parser.parse_args()

    delete_harakat = not args.keep_harakat

    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if args.input_file.endswith('.json'):
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    for field in ['target_text', 'text', 'ar', 'arabic', 'source_text']:
                        if field in item and isinstance(item[field], str):
                            item[field] = process_arabic_text(
                                item[field],
                                max_line_len=args.wrap_width,
                                force_rtl=args.force_rtl,
                                delete_harakat=delete_harakat
                            )
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, str):
                        data[k] = process_arabic_text(
                            v,
                            max_line_len=args.wrap_width,
                            force_rtl=args.force_rtl,
                            delete_harakat=delete_harakat
                        )
            out_str = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            lines = content.splitlines(keepends=True)
            out_str = "".join([
                process_arabic_text(line, max_line_len=args.wrap_width, force_rtl=args.force_rtl, delete_harakat=delete_harakat)
                for line in lines
            ])

        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(out_str)
            print(f"Processed output saved to: {args.output_file}")
        else:
            print(out_str)

    elif args.text:
        res = process_arabic_text(
            args.text,
            max_line_len=args.wrap_width,
            force_rtl=args.force_rtl,
            delete_harakat=delete_harakat
        )
        print(res)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
