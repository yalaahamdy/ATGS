"""
ط£ط¯ط§ط© ط¯ظ…ط¬ ط§ظ„ط®ط· ط§ظ„ط¨ظٹظƒط³ظ„ظٹ ط§ظ„ط¹ط±ط¨ظٹ ظ…ط¹ ط£ظٹ ط£ط·ظ„ط³ ط®ط·ظˆط· (Font Atlas) ظ„ط£ظٹ ظ„ط¹ط¨ط© ط¨ظٹظƒط³ظ„.
طھظ‚ظˆظ… ظ‡ط°ظ‡ ط§ظ„ط£ط¯ط§ط© ط¨ظپطھط­ ظ…ظ„ظپ طµظˆط±ط© ط§ظ„ط®ط· ط§ظ„ط®ط§طµ ط¨ط§ظ„ظ„ط¹ط¨ط© ط§ظ„ظ‡ط¯ظپ (font.png)طŒ
ظˆط¯ظ…ط¬ ط®ط±ظٹط·ط© ط§ظ„ط­ط±ظˆظپ ط§ظ„ط¹ط±ط¨ظٹط© ط§ظ„ط¨ظٹظƒط³ظ„ظٹط© ط§ظ„ظ†ظ‚ظٹط© ط¨ط¯ظ‚ط© 1:1 ط¯ظˆظ† ط£ظٹ ط¶ط¨ط§ط¨ظٹط© ط£ظˆ طھط¯ط§ط®ظ„.
"""

import sys
import os
from PIL import Image

def merge_font(target_font_path, output_path=None, v_offset=210):
    if not os.path.exists(target_font_path):
        print(f"Error: Target file not found: {target_font_path}")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    arabic_strip_path = os.path.join(script_dir, "arabic_pixel_glyphs_strip.png")

    if not os.path.exists(arabic_strip_path):
        print(f"Error: Arabic glyphs strip not found at {arabic_strip_path}")
        return False

    target_img = Image.open(target_font_path).convert("RGBA")
    arabic_strip = Image.open(arabic_strip_path).convert("RGBA")

    # طھط£ظƒط¯ ظ…ظ† ط£ظ† ط§ظ„ط­ط¬ظ… ظƒط§ظپظچطŒ ط£ظˆ ظˆط³ظ‘ط¹ ط§ظ„طµظˆط±ط© ط±ط£ط³ظٹط§ظ‹ ط¥ط°ط§ ظ„ط²ظ…
    req_w = max(target_img.width, arabic_strip.width)
    req_h = max(target_img.height, v_offset + arabic_strip.height)

    if req_w > target_img.width or req_h > target_img.height:
        new_canvas = Image.new("RGBA", (req_w, req_h), (0, 0, 0, 0))
        new_canvas.paste(target_img, (0, 0))
        target_img = new_canvas

    # ط¯ظ…ط¬ ط´ط±ظٹط· ط§ظ„ط­ط±ظˆظپ
    target_img.paste(arabic_strip, (0, v_offset), arabic_strip)

    if output_path is None:
        output_path = target_font_path

    target_img.save(output_path)
    print(f"Success! Arabic pixel font merged into: {output_path} at v={v_offset}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ط§ظ„ط§ط³طھط®ط¯ط§ظ…:")
        print("  python merge_to_font_atlas.py <ظ…ط³ط§ط±_ط®ط·_ط§ظ„ظ„ط¹ط¨ط©.png> [ظ…ط³ط§ط±_ط§ظ„ط­ظپط¸]")
    else:
        target = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        merge_font(target, out)
