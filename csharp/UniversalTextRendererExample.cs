using System;

namespace ATGS.Core
{
    /// <summary>
    /// ظ†ظ…ظˆط°ط¬ طھط·ط¨ظٹظ‚ظٹ ظ…ط¨ط³ط· ظٹظˆط¶ط­ ظƒظٹظپظٹط© ط¯ظ…ط¬ ظ†ط¸ط§ظ… ط§ظ„ط®ط· ط§ظ„ط¨ظٹظƒط³ظ„ظٹ ط§ظ„ط¹ط±ط¨ظٹ
    /// ظپظٹ ط£ظٹ ظ…ط­ط±ظƒ ط£ظ„ط¹ط§ط¨ (Unity, MonoGame, Raylib, Silk.NET, OpenGL, Godot).
    /// </summary>
    public static class UniversalTextRendererExample
    {
        /// <summary>
        /// ظ…ط«ط§ظ„ ط¹ظ„ظ‰ ط¯ط§ظ„ط© ط­ط³ط§ط¨ ط¹ط±ط¶ ط§ظ„ظ†طµ ط¨ط¯ظ‚ط© ط§ظ„ط¨ظٹظƒط³ظ„
        /// </summary>
        public static int MeasureTextWidth(string text, int scale = 1, int defaultCharWidth = 8)
        {
            if (string.IsNullOrEmpty(text)) return 0;

            // 1. طھط´ظƒظٹظ„ ط§ظ„ظ†طµ ظˆط¹ظƒط³ظ‡
            string processed = ArabicSupport.ProcessLine(text);

            int width = 0;
            foreach (char c in processed)
            {
                // ط¥ط°ط§ ظƒط§ظ† ط§ظ„ط­ط±ظپ ط¹ط±ط¨ظٹط§ظ‹طŒ ط®ط° ظ…ط³ط§ظپط© ط§ظ„طھظ‚ط¯ظ… ط§ظ„ط®ط§طµط© ط¨ظ‡
                if (ArabicGlyphs.TryGetGlyph(c, out var glyph))
                {
                    width += glyph.advance * scale;
                }
                else
                {
                    // ط§ظ„ط­ط±ظپ ط§ظ„ط¥ظ†ط¬ظ„ظٹط²ظٹ ط£ظˆ ط§ظ„ط±ظ…ط² ط§ظ„ط§ظپطھط±ط§ط¶ظٹ
                    width += defaultCharWidth * scale;
                }
            }
            return width;
        }

        /// <summary>
        /// ظ…ط«ط§ظ„ طھط¬ط±ظٹط¯ظٹ ط¹ظ„ظ‰ ط¯ط§ظ„ط© ط±ط³ظ… ط§ظ„ظ†طµ
        /// </summary>
        public static void DrawText(string text, int startX, int startY, int scale = 1, int defaultCharWidth = 8, int defaultCharHeight = 11)
        {
            if (string.IsNullOrEmpty(text)) return;

            // 1. ط§ظ„طھط´ظƒظٹظ„ ظˆط¥ط¹ط§ط¯ط© ط§ظ„طھط±طھظٹط¨ (Shaping & BiDi)
            string processed = ArabicSupport.ProcessLine(text);

            int currentX = startX;
            int currentY = startY;

            foreach (char c in processed)
            {
                // ظ…ط¹ط§ظ„ط¬ط© ط§ظ„ط£ط³ط·ط± ط§ظ„ط¬ط¯ظٹط¯ط©
                if (c == '\n')
                {
                    currentX = startX;
                    currentY += (defaultCharHeight + 2) * scale;
                    continue;
                }

                // 2. ظپط­طµ ظ‡ظ„ ط§ظ„ط­ط±ظپ ط¹ط±ط¨ظٹ ظˆظ„ظ‡ ط±ط³ظ… ط¨ظٹظƒط³ظ„ظٹ ظپظٹ ط§ظ„ظ‚ط§ظ…ظˆط³
                if (ArabicGlyphs.TryGetGlyph(c, out var glyph))
                {
                    if (glyph.w > 0)
                    {
                        // ط±ط³ظ… ط§ظ„ط­ط±ظپ ط§ظ„ط¨ظٹظƒط³ظ„ظٹ ظ…ظ† ط§ظ„ط£ط·ظ„ط³
                        // ظ…ظ„ط§ط­ط¸ط©: ط§ط³طھط¨ط¯ظ„ ط¯ط§ظ„ط© DrawQuad ط¨ط¯ط§ظ„ط© ط§ظ„ط±ط³ظ… ط§ظ„ط®ط§طµط© ط¨ظ…ط­ط±ظƒ ظ„ط¹ط¨طھظƒ
                        DrawQuad(
                            destX: currentX + (glyph.xOffset * scale),
                            destY: currentY + (glyph.yOffset * scale),
                            destW: glyph.w * scale,
                            destH: glyph.h * scale,
                            srcU: glyph.u,
                            srcV: glyph.v,
                            srcW: glyph.w,
                            srcH: glyph.h
                        );
                    }

                    // 3. طھط­ط±ظٹظƒ ط§ظ„ظ…ط¤ط´ط± ط¨ط§ظ„ظ…ط³ط§ظپط© ط§ظ„ط¯ظ‚ظٹظ‚ط© ظ„ظ„ط­ط±ظپ ظ„طھظپط§ط¯ظٹ ط£ظٹ ظپط±ط§ط؛ط§طھ
                    currentX += glyph.advance * scale;
                }
                else
                {
                    // ط±ط³ظ… ط§ظ„ط­ط±ظˆظپ ط§ظ„ظ„ط§طھظٹظ†ظٹط© ط£ظˆ ط§ظ„ط£ط±ظ‚ط§ظ… ط§ظ„ط§ظپطھط±ط§ط¶ظٹط© ظ„ظ„ط¹ط¨ط©
                    DrawDefaultChar(c, currentX, currentY, scale);
                    currentX += defaultCharWidth * scale;
                }
            }
        }

        private static void DrawQuad(int destX, int destY, int destW, int destH, int srcU, int srcV, int srcW, int srcH)
        {
            // ط§ط³طھط¯ط¹ط§ط، ط¯ط§ظ„ط© ط§ظ„ط±ط³ظ… ظپظٹ ظ…ط­ط±ظƒ ظ„ط¹ط¨طھظƒطŒ ظ…ط«ط§ظ„:
            // SpriteBatch.Draw(fontAtlas, new Rectangle(destX, destY, destW, destH), new Rectangle(srcU, srcV, srcW, srcH), Color.White);
        }

        private static void DrawDefaultChar(char c, int x, int y, int scale)
        {
            // ط±ط³ظ… ط§ظ„ط­ط±ظپ ط§ظ„ظ„ط§طھظٹظ†ظٹ ط§ظ„ط§ظپطھط±ط§ط¶ظٹ ظ„ظ„ط¹ط¨ط©
        }
    }
}
