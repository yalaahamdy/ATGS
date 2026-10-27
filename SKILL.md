---
name: atgs
description: >-
  Universal Arabic Game Localization & Translation Skill. Provides an end-to-end pipeline
  for game string extraction, AI batch preparation, context preservation, Arabic shaping,
  BiDi reversal for LTR engines (Unity uGUI/TMP/Godot/Custom), tag-safe rich text protection,
  multiline wrapping, and pixel art font atlas merging.
---

# ATGS (Arabic Translate Game Skill)

مهارة تعريب وتوطين ألعاب الفيديو للغة العربية الشاملة لمساعدي الذكاء الاصطناعي والمطورين.

--------------------------------------------------------------------------------

## نظرة عامة (Overview)

تُعد مهارة **ATGS** حلاً تقنياً متكاملاً لتجاوز جميع العقبات الهندسية التي تواجه تعريب ألعاب الفيديو إلى اللغة العربية، بما في ذلك:
1. **استخراج ومعالجة ملفات الألعاب**: التعامل مع مختلف الصيغ (TSV, CSV, JSON, PO, Heaps, Flat Text) دون فقدان المعرفات أو المتغيرات.
2. **إعداد حزم الترجمة السياقية بالذكاء الاصطناعي**: تجزئة النصوص مع شروحات السياق لتسهيل الترجمة الآلية الدقيقة.
3. **محرك التشكيل العربي وBiDi المتقدم**: معالجة مشكلة انفصال الحروف وانعكاس الاتجاه في محركات الألعاب الغربية التي تفتقر لدعم RTL الأصلي (مثل Unity Legacy uGUI).
4. **حماية الوسوم الغنية (Tag-Safe Engine)**: حماية وسوم التنسيق `<color>`, `<b>`, `<i>`, `<size>` من التشوه أو الانقلاب.
5. **التفاف الأسطر متعددة الأسطر الآمن (Multiline Word-Wrapping)**: منع انقلاب ترتيب الأسطر رأسياً في صناديق النصوص الطويلة.
6. **حزمة ألعاب البيكسل والريترو (Pixel Art Toolkit)**: دمج خطوط البيكسل العربية بدقة 1:1 في أطلس خطوط اللعبة مع مكتبات C# للتشغيل اللحظي.

--------------------------------------------------------------------------------

## متى تستخدم مهارة ATGS؟ (When to Use)

- عندما يُطلب منك فحص، استخراج، أو تعريب أي لعبة فيديو إلى اللغة العربية.
- عند التعامل مع ألعاب تعمل بمحرك **Unity** وتظهر فيها نصوص العربية مفككة (`م ر ح ب ا`) أو معكوسة (`ابحرم`).
- عند تعريب ألعاب البيكسل (Pixel-Art / 2D Retro Games) مثل ألعاب GameMaker, MonoGame, Godot, FNA.
- عندما ترغب في تحضير ملفات اللعبة لإرسالها لنماذج الذكاء الاصطناعي للترجمة السياقية مع ضمان استعادتها بدقة 100%.

--------------------------------------------------------------------------------

## خريطة أدوات ATGS (Tools & Directory Structure)

```
ATGS/
├── scripts/
│   ├── atgs_cli.py            # واجهة سطر الأوامر الموحدة الشاملة
│   ├── atgs_reshaper.py       # محرك التشكيل، BiDi، حماية الوسوم، والتفاف الأسطر
│   ├── atgs_extract.py        # أداة استخراج النصوص وإنشاء حزم الترجمة
│   ├── atgs_import.py         # أداة دمج التراجم وإعادة بناء ملفات اللعبة
│   └── merge_to_font_atlas.py # أداة دمج خط البيكسل العربي في Font Atlas
├── csharp/
│   ├── ArabicSupport.cs       # مكتبة C# للتشكيل والـ BiDi اللحظي في المحركات
│   ├── ArabicGlyphs.cs        # خريطة إحداثيات ومسافات الخط البيكسلي العربي
│   └── UniversalTextRendererExample.cs # نموذج تطبيقي للرسم في أي محرك C#
├── pixel_toolkit/
│   └── arabic_pixel_glyphs_strip.png # شريط خط البيكسل العربي الأصلي (1:1 Pixel Art)
└── docs/
    ├── ARABIC_LOCALIZATION_GUIDE.md  # الدليل الهندسي الشامل لتعريب الألعاب
    ├── PIXEL_GAMES_GUIDE.md          # الدليل الاحترافي لتعريب ألعاب البيكسل
    ├── UNITY_UGUI_SOLUTIONS.md       # حلول محركات Unity و uGUI و TextMeshPro
    └── CASE_STUDY_DYSON_SPHERE_PROGRAM.md # دراسة حالة تفصيلية لـ Dyson Sphere Program
```

--------------------------------------------------------------------------------

## أوامر الاستخدام السريع (Quickstart CLI)

### 1. استخراج نصوص اللعبة وتوليد حزم الذكاء الاصطناعي
```bash
python scripts/atgs_cli.py extract "<مسار_مجلد_اللعبة_أو_التوطين>" -o "./atgs_batches" -b 150
```
- يقوم بمسح جميع الملفات، حماية المتغيرات `{0}` والوسوم، وإنشاء `batch_001.json`, `batch_002.json` وخريطة `id_mapping.json`.

### 2. تشكيل وعكس النصوص العربية لمحركات LTR (Unity uGUI)
```bash
# تشكيل نص مفرد مع التفاف الأسطر
python scripts/atgs_cli.py reshape "أهلاً بك أيها القائد في نظام دايسون!" -w 55

# تشكيل ملف كامل (JSON أو TXT)
python scripts/atgs_cli.py reshape -i "translations.json" -o "translations_shaped.json" -w 55
```

### 3. استيراد الترجمات وإعادة بناء ملفات اللعبة
```bash
python scripts/atgs_cli.py import "./atgs_batches/translation_batches" "./atgs_batches/import_mapping/id_mapping.json" -o "<مسار_مجلد_اللعبة_الجديد>" --encoding utf-16le
```
- يقوم بدمج الترجمات، وتطبيق التشكيل التلقائي، وحفظ الملفات بالترميز المطلوب (مثل UTF-16LE لـ Unity TSV).

### 4. دمج خط البيكسل العربي مع أطلس خطوط اللعبة
```bash
python scripts/atgs_cli.py pixel-merge "<مسار_font_atlas.png>" -o "<مسار_الناتج.png>" --v-offset 210
```

--------------------------------------------------------------------------------

## القواعد الذهبية لتعريب الألعاب (Golden Rules)

1. **لا تعكس النص الخام مباشرة إذا كان يحتوي على وسوم Rich Text**:
   - استخدام `atgs_reshaper.py` يضمن بقاء الوسوم مثل `<color=...>` سليمة وعكس ترتيب ظهورها بدقة.
2. **تجنب تراكب حركات التشكيل في الخطوط غير المتخصصة**:
   - استخدم `delete_harakat: true` في خطوط واجهات Unity العادية لتفادي الفجوات البصرية بين الحروف.
3. **التفاف الأسطر المسبق (Pre-Wrapping)**:
   - في النصوص الطويلة، قم بتقسيم الأسطر قبل التشكيل والعكس لتفادي انقلاب ترتيب الأسطر من أسفل لأعلى.
4. **التحقق من ترميز الملفات الدقيق**:
   - محركات الألعاب حساسة جداً للترميز؛ تأكد مما إذا كان المحرك يتطلب `UTF-16LE` (مع أو بدون BOM) أو `UTF-8 with BOM`.
