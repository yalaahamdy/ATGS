using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace ATGS.Core
{
    /// <summary>
    /// ظ†ط¸ط§ظ… ظ…ط¹ط§ظ„ط¬ط© ظˆطھط´ظƒظٹظ„ ط§ظ„ظ†طµظˆطµ ط§ظ„ط¹ط±ط¨ظٹط© ظ„ظ„ط£ظ„ط¹ط§ط¨ (Shaping & Bi-directional Processing)
    /// ظٹظ‚ظˆظ… ط¨ط±ط¨ط· ط§ظ„ط­ط±ظˆظپ ط§ظ„ط¹ط±ط¨ظٹط© ط¨ط£ط´ظƒط§ظ„ظ‡ط§ ط§ظ„ط£ط±ط¨ط¹ط© (ط¨ط¯ط§ظٹط©طŒ ظˆط³ط·طŒ ظ†ظ‡ط§ظٹط©طŒ ظ…ظ†ظپطµظ„)
    /// ظˆط¹ظƒط³ ط§طھط¬ط§ظ‡ ط§ظ„ظ‚ط±ط§ط،ط© ظ…ظ† ط§ظ„ظٹظ…ظٹظ† ط¥ظ„ظ‰ ط§ظ„ظٹط³ط§ط± ظ…ط¹ ط§ظ„ط­ظپط§ط¸ ط§ظ„طھط§ظ… ط¹ظ„ظ‰ ط§ظ„ظƒظ„ظ…ط§طھ ط§ظ„ظ„ط§طھظٹظ†ظٹط© ظˆط§ظ„ط£ط±ظ‚ط§ظ… ظˆط§ظ„ظˆط³ظˆظ….
    /// </summary>
    public static class ArabicSupport
    {
        private struct CharForm
        {
            public char isolated;
            public char final;
            public char initial;
            public char medial;
            public bool connectsNext;

            public CharForm(char iso, char fin, char ini, char med, bool connNext)
            {
                isolated = iso;
                final = fin;
                initial = ini;
                medial = med;
                connectsNext = connNext;
            }
        }

        private static readonly Dictionary<char, CharForm> charForms = new Dictionary<char, CharForm>(50)
        {
            { '\u0621', new CharForm('\uFE80', '\uFE80', '\uFE80', '\uFE80', false) }, // ط،
            { '\u0622', new CharForm('\uFE81', '\uFE82', '\uFE81', '\uFE82', false) }, // ط¢
            { '\u0623', new CharForm('\uFE83', '\uFE84', '\uFE83', '\uFE84', false) }, // ط£
            { '\u0624', new CharForm('\uFE85', '\uFE86', '\uFE85', '\uFE86', false) }, // ط¤
            { '\u0625', new CharForm('\uFE87', '\uFE88', '\uFE87', '\uFE88', false) }, // ط¥
            { '\u0626', new CharForm('\uFE89', '\uFE8A', '\uFE8B', '\uFE8C', true) },  // ط¦
            { '\u0627', new CharForm('\uFE8D', '\uFE8E', '\uFE8D', '\uFE8E', false) }, // ط§
            { '\u0628', new CharForm('\uFE8F', '\uFE90', '\uFE91', '\uFE92', true) },  // ط¨
            { '\u0629', new CharForm('\uFE93', '\uFE94', '\uFE93', '\uFE94', false) }, // ط©
            { '\u062A', new CharForm('\uFE95', '\uFE96', '\uFE97', '\uFE98', true) },  // طھ
            { '\u062B', new CharForm('\uFE99', '\uFE9A', '\uFE9B', '\uFE9C', true) },  // ط«
            { '\u062C', new CharForm('\uFE9D', '\uFE9E', '\uFE9F', '\uFEA0', true) },  // ط¬
            { '\u062D', new CharForm('\uFEA1', '\uFEA2', '\uFEA3', '\uFEA4', true) },  // ط­
            { '\u062E', new CharForm('\uFEA5', '\uFEA6', '\uFEA7', '\uFEA8', true) },  // ط®
            { '\u062F', new CharForm('\uFEA9', '\uFEAA', '\uFEA9', '\uFEAA', false) }, // ط¯
            { '\u0630', new CharForm('\uFEAB', '\uFEAC', '\uFEAB', '\uFEAC', false) }, // ط°
            { '\u0631', new CharForm('\uFEAD', '\uFEAE', '\uFEAD', '\uFEAE', false) }, // ط±
            { '\u0632', new CharForm('\uFEAF', '\uFEB0', '\uFEAF', '\uFEB0', false) }, // ط²
            { '\u0633', new CharForm('\uFEB1', '\uFEB2', '\uFEB3', '\uFEB4', true) },  // ط³
            { '\u0634', new CharForm('\uFEB5', '\uFEB6', '\uFEB7', '\uFEB8', true) },  // ط´
            { '\u0635', new CharForm('\uFEB9', '\uFEBA', '\uFEBB', '\uFEBC', true) },  // طµ
            { '\u0636', new CharForm('\uFEBD', '\uFEBE', '\uFEBF', '\uFEC0', true) },  // ط¶
            { '\u0637', new CharForm('\uFEC1', '\uFEC2', '\uFEC3', '\uFEC4', true) },  // ط·
            { '\u0638', new CharForm('\uFEC5', '\uFEC6', '\uFEC7', '\uFEC8', true) },  // ط¸
            { '\u0639', new CharForm('\uFEC9', '\uFECA', '\uFECB', '\uFECC', true) },  // ط¹
            { '\u063A', new CharForm('\uFECD', '\uFECE', '\uFECF', '\uFED0', true) },  // ط؛
            { '\u0641', new CharForm('\uFED1', '\uFED2', '\uFED3', '\uFED4', true) },  // ظپ
            { '\u0642', new CharForm('\uFED5', '\uFED6', '\uFED7', '\uFED8', true) },  // ظ‚
            { '\u0643', new CharForm('\uFED9', '\uFEDA', '\uFEDB', '\uFEDC', true) },  // ظƒ
            { '\u0644', new CharForm('\uFEDD', '\uFEDE', '\uFEDF', '\uFEE0', true) },  // ظ„
            { '\u0645', new CharForm('\uFEE1', '\uFEE2', '\uFEE3', '\uFEE4', true) },  // ظ…
            { '\u0646', new CharForm('\uFEE5', '\uFEE6', '\uFEE7', '\uFEE8', true) },  // ظ†
            { '\u0647', new CharForm('\uFEE9', '\uFEEA', '\uFEEB', '\uFEEC', true) },  // ظ‡
            { '\u0648', new CharForm('\uFEED', '\uFEEE', '\uFEED', '\uFEEE', false) }, // ظˆ
            { '\u0649', new CharForm('\uFEEF', '\uFEF0', '\uFBE8', '\uFBE9', false) }, // ظ‰
            { '\u064A', new CharForm('\uFEF1', '\uFEF2', '\uFEF3', '\uFEF4', true) },  // ظٹ
            { '\u067E', new CharForm('\uFB56', '\uFB57', '\uFB58', '\uFB59', true) },  // ظ¾
            { '\u0686', new CharForm('\uFB7A', '\uFB7B', '\uFB7C', '\uFB7D', true) },  // ع†
            { '\u0698', new CharForm('\uFB8A', '\uFB8B', '\uFB8A', '\uFB8B', false) }, // عک
            { '\u06AF', new CharForm('\uFB92', '\uFB93', '\uFB94', '\uFB95', true) },  // ع¯
        };

        public static bool HasArabic(string text)
        {
            if (string.IsNullOrEmpty(text)) return false;
            foreach (char c in text)
            {
                if ((c >= '\u0600' && c <= '\u06FF') ||
                    (c >= '\uFB50' && c <= '\uFDFF') ||
                    (c >= '\uFE70' && c <= '\uFEFF'))
                {
                    return true;
                }
            }
            return false;
        }

        public static string Shape(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            StringBuilder sb = new StringBuilder(text.Length);
            for (int i = 0; i < text.Length; i++)
            {
                char c = text[i];
                if (c == '\u0644' && i + 1 < text.Length)
                {
                    char next = text[i + 1];
                    char lamAlef = '\0';
                    bool prevConnectsLam = (i > 0 && charForms.TryGetValue(text[i - 1], out var pf) && pf.connectsNext);

                    if (next == '\u0622') lamAlef = prevConnectsLam ? '\uFEF6' : '\uFEF5';
                    else if (next == '\u0623') lamAlef = prevConnectsLam ? '\uFEF8' : '\uFEF7';
                    else if (next == '\u0625') lamAlef = prevConnectsLam ? '\uFEFA' : '\uFEF9';
                    else if (next == '\u0627') lamAlef = prevConnectsLam ? '\uFEFC' : '\uFEFB';

                    if (lamAlef != '\0')
                    {
                        sb.Append(lamAlef);
                        i++;
                        continue;
                    }
                }

                if (charForms.TryGetValue(c, out var form))
                {
                    bool prevConnects = false;
                    if (i > 0)
                    {
                        char prevChar = text[i - 1];
                        if (charForms.TryGetValue(prevChar, out var pf))
                            prevConnects = pf.connectsNext;
                    }

                    bool nextConnects = false;
                    if (i + 1 < text.Length)
                    {
                        char nextChar = text[i + 1];
                        nextConnects = charForms.ContainsKey(nextChar);
                    }

                    if (prevConnects && nextConnects && form.connectsNext)
                        sb.Append(form.medial);
                    else if (prevConnects)
                        sb.Append(form.final);
                    else if (nextConnects && form.connectsNext)
                        sb.Append(form.initial);
                    else
                        sb.Append(form.isolated);
                }
                else
                {
                    sb.Append(c);
                }
            }
            return sb.ToString();
        }

        public static string Reverse(string text)
        {
            if (string.IsNullOrEmpty(text)) return text;

            // ط­ظ…ط§ظٹط© ط§ظ„ظ†طµظˆطµ ط§ظ„ظ„ط§طھظٹظ†ظٹط© ظˆط§ظ„ط£ط±ظ‚ط§ظ… ظˆط§ظ„ظˆط³ظˆظ… ظ…ظ† ط§ظ„ط§ظ†ط¹ظƒط§ط³
            var tokens = new List<string>();
            var tokenPattern = new Regex(@"(\{[0-9]+\}|%[a-zA-Z0-9]+|<[^>]+>|[a-zA-Z0-9_\-\.\:\/]+|[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]+|\s+|[^\s\w])");
            var matches = tokenPattern.Matches(text);

            if (matches.Count == 0)
            {
                char[] arr = text.ToCharArray();
                Array.Reverse(arr);
                return new string(arr);
            }

            for (int i = 0; i < matches.Count; i++)
            {
                tokens.Add(matches[i].Value);
            }

            tokens.Reverse();

            StringBuilder sb = new StringBuilder(text.Length);
            foreach (var token in tokens)
            {
                if (HasArabic(token))
                {
                    char[] arr = token.ToCharArray();
                    Array.Reverse(arr);
                    sb.Append(arr);
                }
                else
                {
                    // ط£ظ‚ظˆط§ط³ ط§ظ„طھظ†ط§ط¸ط±
                    if (token == "(") sb.Append(")");
                    else if (token == ")") sb.Append("(");
                    else if (token == "[") sb.Append("]");
                    else if (token == "]") sb.Append("[");
                    else if (token == "{") sb.Append("}");
                    else if (token == "}") sb.Append("{");
                    else if (token == "<") sb.Append(">");
                    else if (token == ">") sb.Append("<");
                    else sb.Append(token);
                }
            }
            return sb.ToString();
        }

        public static string ProcessLine(string text)
        {
            if (string.IsNullOrEmpty(text) || !HasArabic(text))
                return text;

            string shaped = Shape(text);
            return Reverse(shaped);
        }
    }
}
