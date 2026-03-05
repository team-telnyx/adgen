# Catalog Quality Review — Paperclip

**Date:** 2026-03-05
**Status:** ⏳ Partial — catalog.json not yet committed to repository

## Summary

Coldshot's `catalog.json` has been generated (seen in working state: 2,391 entries, v1) but is not yet committed to this branch. Full review will complete once catalog.json is merged. Below are preliminary findings from the snapshot observed during INDEX.md preparation.

---

## 1. Archived Asset Marking ✅ PASS

**Finding:** All 62 assets in `zold/`, `zArchive/`, and `Archive/` paths were correctly marked `archived: true`. Zero false negatives detected.

**One concern:** 1 asset was marked archived that wasn't in a typical archive path — worth verifying it's intentional vs. a false positive.

---

## 2. Industry Verticals ⚠️ NEEDS IMPROVEMENT

**Finding:** 8 verticals detected: healthcare (52), logistics (45), travel (44), finance (34), retail (28), insurance (27), restaurant (27), automotive (7).

**Issues:**
- **1,827 assets have no vertical assigned** — many are product-specific (not vertical-specific), but some industry photography in `Photography/Stock_Unsplash (Free)/03_Industry/` (112 files) likely has vertical signal in filenames that isn't being extracted
- **Missing verticals from social assets:** `Industry_Visuals/Social_Assets/` has folders for 7 verticals (Finance, Healthcare, Insurance, Logistics, Restaurants, Retail, Travel) with 8 assets each — these should all have verticals tagged but need to verify coverage
- **"restaurant" vs "restaurants"** — folder uses plural `Restaurants/`, catalog uses singular `restaurant` — minor inconsistency but could affect search

---

## 3. Product Name Consistency ⚠️ NEEDS NORMALIZATION

**Finding:** 11 product names detected. Case is title-case but naming varies:

| Catalog Name | Folder Naming | Frequency | Issue |
|-------------|---------------|-----------|-------|
| Voice Ai | Voice-AI-Agent, Voice_AI | 287 | "Ai" should be "AI" |
| Voice Api | Voice-API | 269 | "Api" should be "API" |
| Esim | eSIM | 260 | Should be "eSIM" |
| Rcs | RCS | 239 | Should be "RCS" |
| Ai Assistant | AI-Assistant | 223 | Should be "AI Assistant" |
| Iot | IoT-SIM-Card | 26 | Should be "IoT" |
| Mobile Voice | Mobile-Voice | 11 | OK |
| Sip | SIP-Trunking | 2 | Should be "SIP Trunking" |
| Storage | Storage | 2 | OK |
| Object Storage | — | 2 | Duplicate of Storage? |
| Networking | — | 1 | OK |

**Recommendation:** Normalize to official Telnyx product names:
- `Voice AI Agent` (not "Voice Ai")
- `Voice API` (not "Voice Api")
- `eSIM` (not "Esim")
- `RCS` (not "Rcs")
- `AI Assistant` (not "Ai Assistant")
- `IoT SIM` (not "Iot")
- `SIP Trunking` (not "Sip")
- Merge `Storage` and `Object Storage`

---

## 4. Dimensions Extraction ❌ NEEDS WORK

**Finding:** Only 23 of 2,391 assets have dimensions extracted. 2,368 are missing.

**Root cause:** Dimensions are only extracted from explicit `WIDTHxHEIGHT` patterns in filenames (e.g., `900x620`, `1200x571`). The catalog does NOT:
- Parse aspect ratio indicators (`16x9`, `1x1`, `3x2`) into actual pixel dimensions
- Read image file headers for actual dimensions
- Infer dimensions from `@2x` retina suffixes

**Impact:** ~80+ assets have dimension/aspect info in filenames that isn't being captured:
- `*_16x9.png` files → should map to standard dimensions
- `*_1x1.png` files → square format
- `*_3x2.png` files → landscape format
- `*_900x620.png` files → explicit (these ARE captured)
- `*@2x.*` files → double resolution variant

**Recommendation:**
1. Add aspect ratio parsing: `16x9` → `1920x1080`, `1x1` → `1080x1080`, `3x2` → `1200x800`
2. Use `Pillow` or `imagemagick` to read actual pixel dimensions from file headers
3. Mark `@2x` variants with a `retina: true` flag

---

## 5. Additional Observations

### Format Field
The `format` field is `null` for almost all assets despite file extensions being present. Should populate from file extension (`.png` → `PNG`, `.jpg` → `JPEG`, `.webp` → `WebP`, `.svg` → `SVG`).

### Usable_for Field
Most assets have only `["general"]` — this is too generic for effective matching. Should be enriched:
- Photography → `["blog_hero", "social_post", "email_header", "case_study"]`
- Product features → `["product_ad", "feature_comparison", "linkedin_carousel"]`
- Icons → `["icon_overlay", "email_icon", "ui_element"]`
- Patterns → `["background", "ad_fill", "presentation"]`

### Source File Pollution
257 assets in `Source Files/`, `Motion Source File/`, `Working file/` directories are included in the catalog. These are production source files (After Effects assets, ScreenStudio cursors), not usable ad assets. They should either be:
- Excluded from the catalog entirely, OR
- Marked with `type: "source_file"` and excluded from search

### Description Quality
Descriptions are auto-generated templates like "Voice ai product, visual, suitable for general, depicting [filename]". These are too generic for semantic search. Better approach:
- Extract feature names from folder structure (e.g., "Warm transfers" feature visual)
- Include industry context when available
- Reference ad format suitability

---

## Action Items for Coldshot

| # | Priority | Item | Impact |
|---|----------|------|--------|
| 1 | 🔴 High | Normalize product names to official casing | Search accuracy |
| 2 | 🔴 High | Exclude or flag source files (257 assets) | Search noise reduction |
| 3 | 🟡 Medium | Extract dimensions from file headers | Format matching |
| 4 | 🟡 Medium | Parse aspect ratios from filenames | Ad format selection |
| 5 | 🟡 Medium | Populate format field from extensions | Basic metadata |
| 6 | 🟢 Low | Enrich usable_for beyond "general" | Search relevance |
| 7 | 🟢 Low | Improve auto-generated descriptions | Semantic search quality |
| 8 | 🟢 Low | Add vertical tagging to industry photography | Vertical campaign matching |

---

*Full review will be updated once catalog.json is committed and available for deeper analysis.*
