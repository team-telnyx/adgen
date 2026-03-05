# Brand Asset Library

> **2,391 assets** across 37 categories | **2,328 active** | **63 archived**
> Generated: 2026-03-05 | Semantic search: `scripts/search_library.py`

## How to Use This Library

When creating ads, search by: **persona, industry, product, format, theme**.
Prefer library assets over AI-generated images when a match exists (score > 0.8).

**Programmatic search:**
```bash
echo '{"query": "healthcare hero image for LinkedIn", "limit": 5}' | python3 scripts/search_library.py
```

**Pipeline integration:** `scripts/pipeline.py` automatically searches the library before generating AI hero images. If a library asset scores > 0.8 for the brief context, it uses the real brand asset instead.

**Feedback loop:** Record which assets work well per persona to improve future selections:
```bash
echo '{"action": "record", "asset_path": "...", "persona": "cio_healthcare", "rating": "positive"}' | python3 scripts/feedback_loop.py
```

---

## Categories by Use Case

### Hero Images (83 assets)
High-impact visuals for ad headers, landing pages, and featured images.
- **Products:** Voice AI Agent, Voice API, eSIM, RCS, Mobile Voice, IoT, SIP, Storage, Networking
- **Industries:** Healthcare, Finance, Travel, Retail, Insurance, Logistics, Restaurants, Automotive
- **Formats:** Landscape (primary), with SEO/mobile variants per industry
- **Best for:** LinkedIn ads, Google Display, blog featured images, landing page heroes
- **Collections:** `_NEW_Collection_Industry-Heroes/`, `_NEW_Collection_Product-Heroes/`, `Industry_Visuals/Industry_Hero/`

### Product Features (70 assets)
Detail shots showing specific product capabilities and UI.
- **Products:** Voice AI Agent, Voice API
- **Formats:** Landscape
- **Best for:** Blog posts, case studies, product pages, LinkedIn carousels
- **Collections:** `_NEW_Collection_Product-Features/`, `Product_Visuals/`

### Social Assets (84 assets)
Purpose-built for social media campaigns, sized for platform specs.
- **Industries:** Healthcare, Finance, Travel, Retail, Insurance, Logistics, Restaurants
- **Best for:** LinkedIn posts, Meta ads, Twitter cards, Instagram
- **Collections:** `Industry_Visuals/Social_Assets/`, `Homepage_Visuals_*/Use-Cases-Block/Social/`

### Icons & Patterns (1,275+ assets)
Product iconography (static + animated frames), brand patterns, industry icons.
- **Products:** Voice AI, Voice API, eSIM, RCS, AI
- **Variants:** Colorful, Black, Pattern, Lockup (per product)
- **Best for:** Email headers, presentations, UI elements, ad overlays, social posts
- **Collections:** `Iconography/`, `_NEW_Collection_Product-Icons/`, `Brand_Patterns/`

### Photography (353 assets)
Stock and custom photography organized by industry and use case.
- **Industries:** Healthcare, Finance, Travel, Retail, Insurance, Logistics, Restaurants, Automotive
- **Best for:** Blog featured images, LinkedIn ads, landing pages, case studies
- **Collections:** `Photography/`, `_NEW_Collection_Use-Cases/*/Photography/`

### Brand Visuals (382 assets)
General brand imagery, homepage sections, enterprise blocks, event promos.
- **Products:** AI Assistant, Voice AI, Voice API, IoT
- **Themes:** Dark, Light
- **Best for:** Website sections, presentations, brand collateral
- **Collections:** `Brand_Visuals/`, `Homepage_Visuals_*/`, `Telnyx.com_Sections/`

### Backgrounds & Patterns (43 assets)
Gradient backgrounds, brand patterns (solid, outline, multiplied).
- **Themes:** Dark (primary)
- **Best for:** Ad backgrounds, presentation slides, landing page sections
- **Collections:** `Brand_Patterns/`, `Homepage_Visuals_July-2025/6_AI-Products/Background gradients/`

### Promotional Assets (10 assets)
Product promos, widget demos, overview diagrams.
- **Products:** Voice AI Agent, Mobile Voice
- **Formats:** Square
- **Best for:** Social posts, LinkedIn ads, Google Display
- **Collections:** `_NEW_Collection_Product-Promos/`

### How-It-Works & Diagrams (16 assets)
Step-by-step product flow visuals and technical diagrams.
- **Products:** Mobile Voice, eSIM, Object Storage
- **Best for:** Blog posts, documentation, case studies, sales decks
- **Collections:** `_NEW_Collection_Product-How-it-works/`, `_NEW_Collection_Telnyx-Differentiators/`

### Differentiators (12 assets)
Full-stack diagrams, infrastructure visuals highlighting Telnyx advantages.
- **Best for:** Sales decks, competitive comparisons, enterprise pages
- **Collections:** `Differentiators_Visuals/`, `_NEW_Collection_Telnyx-Differentiators/`

### UI Navigation Elements (27 assets)
Header images for website navigation sections (Product, Solutions, Developers, Resources).
- **Industries:** Healthcare, Finance, Logistics, Travel
- **Best for:** Website navigation, product category headers
- **Collections:** `Navigation_Header_September-2025/`

### Maps & Globes (4+ assets)
Geographic infrastructure visuals showing Telnyx global presence.
- **Best for:** Enterprise pages, infrastructure sections, "why Telnyx" content
- **Collections:** `Maps_and_Globes/`, `_NEW_Collection_Globes/`

### Logos & Badges (21 assets)
Customer logos, certification badges (ISO, G2), partnership logos, Telnyx logos.
- **Best for:** Trust sections, case studies, email signatures, partner pages
- **Collections:** `Customer-Logos/`, `Certification_Badges/`, `LowLatencyClub-Logo/`, `G2/`

### Employee Headshots (11 assets)
Team photos for blog author bios and about pages.
- **Collections:** `Employee_Headshots/`

---

## Industry Coverage

| Industry | Hero | Social | Photography | Icons | Total |
|----------|------|--------|-------------|-------|-------|
| Healthcare | ✅ | ✅ | ✅ | ✅ | 50+ |
| Finance | ✅ | ✅ | ✅ | — | 30+ |
| Travel | ✅ | ✅ | ✅ | ✅ | 40+ |
| Retail | ✅ | ✅ | ✅ | ✅ | 30+ |
| Insurance | ✅ | ✅ | ✅ | — | 20+ |
| Logistics | ✅ | ✅ | ✅ | ✅ | 25+ |
| Restaurants | ✅ | ✅ | ✅ | — | 20+ |
| Automotive | ✅ | — | ✅ | — | 15+ |

## Product Coverage

| Product | Hero | Feature | Icons | Promo | How-It-Works |
|---------|------|---------|-------|-------|--------------|
| Voice AI Agent | ✅ | ✅ | ✅ | ✅ | — |
| Voice API | ✅ | ✅ | ✅ | — | — |
| eSIM | ✅ | — | ✅ | — | ✅ |
| RCS | ✅ | — | ✅ | — | — |
| Mobile Voice | ✅ | — | — | ✅ | ✅ |
| AI/AI Assistant | ✅ | — | ✅ | — | — |

---

## Data Files

| File | Purpose | Size |
|------|---------|------|
| `catalog.json` | Structured metadata for every asset | 2,391 entries |
| `embeddings.json` | Semantic embeddings (GTE-Large 1024d) | 2,328 entries |
| `feedback.json` | Usage feedback per persona/asset | Growing |

## Architecture

```
Brief → search_library.py (semantic match)
         ├─ score > 0.8 → USE library asset
         └─ score < 0.8 → generate_image.py (DALL-E/Gemini)
                              ↓
                         pipeline.py → Abyssale render
                              ↓
                         feedback_loop.py (learn from usage)
```
