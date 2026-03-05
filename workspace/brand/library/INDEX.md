# Brand Asset Library — AdGen Reference

## Quick Reference

| Metric | Value |
|--------|-------|
| Total image assets | 2,264 usable (2,521 including source files) |
| Active assets | 2,201 |
| Archived assets | 63 (in zold/zArchive/Archive folders) |
| Products covered | Voice AI Agent, Voice API, Mobile Voice, eSIM, RCS, AI Assistant, IoT, SIP, Storage, Networking |
| Industries covered | Healthcare, Finance, Travel, Retail, Insurance, Logistics, Restaurants, Automotive |
| Format types | PNG, JPG, WebP, SVG |
| Aspect ratios | 16×9, 1×1, 3×2, 900×620, @2x retina |

## How AdGen Uses This Library

1. Brief arrives with persona + campaign context
2. Semantic search finds best matching assets (via catalog.json embeddings)
3. Library match > 0.8 → use real asset (preferred)
4. Library match < 0.8 → generate with DALL-E/Gemini
5. Feedback loop improves matching over time

⚠️ **Archived assets** in `zold/`, `zArchive/`, or `Archive/` folders exist in catalog.json but are marked `archived: true`. Always prefer non-archived versions.

---

## Product Icon Frames & Animations (1,291 assets)

Sequential PNG frames for product icon animations + static icon variants. **This is the largest category by count**, but most files are individual animation frames, not standalone images.

**Products:** AI, Voice AI Agent, Voice API, eSIM, RCS
**Static variants:** Colorful (538 frames across 5 products), Black (5), Black Suite (1), Lockup Black (5), Pattern Colorful (20)
**Animation variants:** Colorful, Black 3D, Black 3D on color background, Black 3D with lockup, Background-only, Complete Loop

**Best for:** Video ad compositions, animated social posts, motion graphics. Use static colorful variants for thumbnail/icon needs. Not suitable as standalone ad images.
**Personas:** Product marketers, motion designers, video ad campaigns

**Paths:**
- `_NEW_Collection_Product-Icons/_NEW_Product-Icon-Static/` — Static rendered frames
- `_NEW_Collection_Product-Icons/_NEW_Product-Icon-Animations/` — Animation sequences

⚠️ 6 assets in `_NEW_Product-Icon-Animations/zold/` — use non-archived versions.

---

## Photography (333 assets)

Stock and original photography organized by use case and industry.

**Subcategories:**
- People + Devices (134) — People using phones, laptops, tech in professional/lifestyle settings
- Industry-specific (112) — Healthcare, finance, logistics, travel, retail scene photography
- People Moments (38) — Candid human moments, team collaboration, conversations
- Use Case scenes (40) — Scenario-based: customer support, field workers, remote teams
- Customer Stories (5) — Brand storytelling photography
- Content Creator Headshots (4) — Author/speaker portraits

**Best for:** Blog featured images, social media posts, case study visuals, landing page hero backgrounds, email headers
**Personas:** Content marketers, blog writers, social media managers, case study authors

**Paths:**
- `Photography/Stock_Unsplash (Free)/` — Free-use stock (329 assets)
- `Photography/Content-Creator_Headshots/` — Author headshots (4 assets)

---

## Product Feature Visuals (85 assets)

Detail shots showing specific product capabilities with UI overlays and feature callouts.

**Products:** Voice AI Agent (9 features × 2 sizes), Voice API (7 features × 3 sizes), Mobile Voice, eSIM, RCS
**Features shown:** Warm transfers, Multi-agent handoffs, MCP Server Support, Noise suppression, Versioning/Canary, Voice playground, Multi-language, HD voice, Call recording, Browser/app calling, STT, TTS, Answering machine, Real-time media streaming
**Formats:** 16×9, 900×620, 1×1, 3×2

**Best for:** Product comparison ads, feature-specific landing pages, LinkedIn carousel posts, Google Display ads highlighting capabilities
**Personas:** Product marketers, demand gen, competitive positioning

**Paths:**
- `_NEW_Collection_Product-Features/01_Voice-AI-Agent/` — Voice AI Agent features
- `_NEW_Collection_Product-Features/02_Voice-API/` — Voice API features
- `_NEW_Collection_Product-Features/03_Mobile-Voice/` through `05_RCS/`

⚠️ ~20 assets in `zold/` subfolders — prefer non-zold versions.

---

## Industry Visuals & Social Assets (76 assets)

Industry-specific hero images and pre-formatted social content.

**Industries:** Healthcare, Finance, Travel, Insurance, Logistics, Restaurants, Retail (7 verticals × 8 social assets = 56 social)
**Hero images:** V1 and V2 sets (8 total)
**Social format:** Ready-to-post industry-specific graphics

**Best for:** Vertical-specific LinkedIn/Facebook ads, industry landing pages, email campaigns targeting specific sectors
**Personas:** Industry marketing leads, vertical campaign managers

**Paths:**
- `Industry_Visuals/Social_Assets/{Industry}/` — 8 assets per vertical
- `Industry_Visuals/Industry_Hero/V1/` and `V2/` — Hero images
- `Industry_Visuals/Solution-Overview_Thumbails/` — Solution thumbnails

⚠️ 9 assets in `Industry_Visuals/zArchive/` — marked archived, skip.

---

## Product & Legacy Page Heroes (64 + 10 assets)

Product detail page heroes and website section visuals.

**Product Visuals (64):** Voice API, SMS API, SIP Trunking, 10DLC, Short Code, Fax API, Global Numbers, Number Lookup, Verify API, Toll-Free, Zoom Phone, Microsoft Teams, IoT SIM Card, Storage, Inference, AI Assistant, Voice AI components
**Format:** Most have both JPG (with background) and PNG (transparent background) variants

**NEW Product Heroes (10):** Voice AI Agent, Voice API, Mobile Voice, eSIM, RCS
**Formats:** 16×9, 1×1, 900×620, 3×2

**Best for:** Product landing pages, product announcement ads, website hero sections
**Personas:** Web team, product marketers, launch campaign managers

**Paths:**
- `Product_Visuals/` — Legacy product detail heroes (with/without transparent backgrounds)
- `_NEW_Collection_Product-Heroes/` — New hero collection by product

⚠️ 1 asset in `Product_Visuals/zold/`, 1 in `_NEW_Collection_Product-Heroes/02_Voice-API/_zold/`.

---

## Homepage & Website Section Visuals (102 + 56 assets)

Website section visuals from two design generations, plus page-section components.

**Homepage April 2025 (64):** AI Assistant demos, enterprise block, infrastructure block, use cases block, hero animation
**Homepage July 2025 (38):** Hero background video, interactive voice demo, customer logos, differentiators, how-it-works, use cases, AI products, sign-up banner
**Telnyx.com Sections (56):** Enterprise pages, event details, hero sections, full-stack interactive, integrations, photography promo carousel, security badges, sign-up banners

**Best for:** Website redesigns, landing page templates, section component reuse
**Personas:** Web designers, landing page builders

**Paths:**
- `Homepage_Visuals_April-2025/`
- `Homepage_Visuals_July-2025/`
- `Telnyx.com_Sections/`

⚠️ ~10 assets in `Homepage_Visuals_July-2025/*/zold/` — prefer non-zold versions.

---

## Use Case Visuals (12 + 33 assets)

Industry use case scenes showing AI in action across verticals.

**NEW Use Cases (12):** Healthcare (7 incl. speech text overlays), Retail (2), Travel (2), Automotive (1)
**Legacy Use Cases (33):** Broader set of use case visuals
**Formats:** 16×9, 1×1, @2x retina

**Best for:** Vertical campaign landing pages, industry-specific ad creative, case study headers
**Personas:** Vertical marketers, case study writers, industry campaign managers

**Paths:**
- `_NEW_Collection_Use-Cases/{Automotive,Finance,Healthcare,Retail,Travel}/`
- `Use_Case_Visuals/`

---

## Navigation Headers (27 assets)

Website navigation header images for product sections.

**Sections:** Developers, Product, Resources, Solutions, Why Telnyx

**Best for:** Website navigation, section headers
**Personas:** Web team

**Path:** `Navigation_Header_September-2025/`

---

## Brand Patterns & Backgrounds (17 assets)

Telnyx brand patterns in multiple colorways for ad backgrounds and compositions.

**Styles:** Solid one-color, Solid two-color, Solid multicolor, Outline, Multiplied, Application-specific

**Best for:** Ad background fills, email templates, presentation slides, social post backgrounds
**Personas:** Designers, ad creative builders, email marketers

**Path:** `Brand_Patterns/`

---

## Product Promos & How-It-Works (15 + 12 assets)

Promotional visuals and step-by-step product explainers.

**Promos (15):** Voice AI Agent, Mobile Voice
**How-It-Works (12):** Mobile Voice (4 steps), eSIM (5 steps) — sequential step visuals showing product setup flow

**Best for:** Product tutorial ads, onboarding sequences, explainer carousels
**Personas:** Product marketers, onboarding designers

**Paths:**
- `_NEW_Collection_Product-Promos/`
- `_NEW_Collection_Product-How-it-works/`

---

## Icons & Iconography (13 assets)

Small-format icons for products, industries, resources, and social platforms.

**Types:** Industry icons (Healthcare, Logistics, Travel, Retail, Finance), Social icons (LinkedIn, Twitter, Facebook), Resource icons (Docs, Ebook, Webinar, Tutorial, Article)

**Best for:** Ad icon overlays, email template icons, navigation elements
**Personas:** Email designers, UI designers

**Path:** `Iconography/`

---

## Logos, Badges & Trust Signals (18 assets)

Customer logos, G2 comparison charts, certification badges.

**G2 (7):** Summer 2023 + Fall 2023 comparison charts (Results, Support, Usability) + hero badges
**Certification Badges (10):** ISO 27001, ISO 27701 (via Dotcom and supplied sources)
**Customer Logos (1):** Audio-Codes (SVG)

**Best for:** Trust sections on landing pages, comparison ads, compliance/security messaging
**Personas:** Demand gen, enterprise sales enablement, compliance marketing

**Paths:**
- `G2/`
- `Certification_Badges/`
- `Customer-Logos/`

---

## Specialized Assets

### Industry Heroes — NEW (5 assets)
Industry-specific hero images: Automotive, Finance, Healthcare, Travel/Hospitality.
**Path:** `_NEW_Collection_Industry-Heroes/`

### Differentiators (6 assets)
Enterprise differentiator visuals: 24/7 Support, Full Stack, Global Scalability. WebP format, @1x and @2x.
**Path:** `Differentiators_Visuals/`

### Blog Visuals (9 assets)
Blog-specific inline and hero visuals for articles on Conversational AI, Voice AI, SIM form factors.
**Path:** `Blog_Visuals/`

### Developer & Community (7 assets)
Dev docs homepage backgrounds, Slack community banners, developer community visuals.
**Paths:** `Dev-Docs_Home_September-2025/`, `Dev_Community_Visuals/`

### EverRoam App (6 assets)
EverRoam mobile app intro screens. JPG, @1x and @2x variants.
**Path:** `EverRoam_App/`

### Social Video / TTS (23 assets)
Text-to-speech related social video assets.
**Path:** `_NEW_Social_Video/TTS/`

### Brand Visuals (4 assets)
Core brand identity: logo lockup, product overview, transparency messaging.
**Path:** `Brand_Visuals/`

### Partner Program (11 assets)
Partner program marketing visuals.
**Path:** `Partner-Program_Visuals/`

### Clawhouse (8 assets)
Clawhouse platform visuals: hero, signup, feature tiles, capability icons (deploy, isolation, memory, models, multichannel, network).
**Path:** `_NEW_Clawhouse/`

### Maps & Globes (6 assets)
Network maps (US data centers, PoPs) and globe renders. PNG + SVG.
**Path:** `Maps_and_Globes/`

### Event Promos (2 assets)
Event promotional materials.
**Path:** `_NEW_Collection_Event-Promos/`

### Telnyx Differentiators — NEW (3 assets)
New differentiator collection visuals.
**Path:** `_NEW_Collection_Telnyx-Differentiators/`

### Employee Headshots (4 assets)
Team member photos.
**Path:** `Employee_Headshots/`

---

## Archived Asset Locations

These folders contain deprecated versions. Catalog marks them `archived: true`. **Always prefer non-archived versions.**

| Location | Count | Notes |
|----------|-------|-------|
| `Homepage_Visuals_July-2025/*/zold/` | ~25 | Old use case and hero variants |
| `_NEW_Collection_Product-Features/*/zold/` | ~20 | Previous feature image versions |
| `Homepage_Visuals_April-2025/*/Archive/` | ~5 | Deprecated homepage assets |
| `Industry_Visuals/zArchive/` | 9 | Old industry visuals |
| `_NEW_Collection_Product-Icons/*/zold/` | 6 | Old icon animations |
| `Product_Visuals/zold/` | 1 | Microsoft Teams legacy |
| `_NEW_Collection_Product-Heroes/02_Voice-API/_zold/` | 1 | Old Voice API hero |

**Total archived:** 63 assets across 7 locations.
