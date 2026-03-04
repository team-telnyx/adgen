# TOOLS.md — AdGen

## render.py

The only code in this system. Takes JSON params, outputs PNG.

### Usage
```bash
echo '{"template": "dark-hero-left", "format": "linkedin_1200x1200", ...}' | python3 scripts/render.py
```

### Input Schema
```json
{
  "template": "dark-hero-left",
  "format": "linkedin_1200x1200",
  "background": "#000000",
  "headline": "Your Headline Here",
  "subhead": "Supporting text",
  "cta": "Talk to Sales",
  "accent_color": "#D4E510",
  "hero_image": "brand/imagery/product/portal-dashboard.png",
  "logo_variant": "wordmark-cream",
  "output": "output/campaign/format.png"
}
```

### Output
PNG file at the specified output path.

## Brand Assets
- Rules: `brand/rules.yaml` — read before every brief
- Colors: `brand/colors.yaml`
- Logos: `brand/logos/` — wordmark-cream.png, wordmark-black.png, icon-cream.png, icon-black.png
- Imagery: `brand/imagery/` — browse `index.md` for tagged catalog

## Image Generation
- **DALL-E:** `openai` Python SDK for abstract/conceptual imagery
- **Nano Banana Pro:** Via nano-banana-pro skill for Gemini image generation
- Only for abstract backgrounds, textures, conceptual visuals
- Never generate faces, products, or photographic scenes

## Abyssale (Multi-Format Export)
- Takes master 1200×1200 PNG + text content + brand assets
- Returns all format variants with intelligent reflow
- Call via Abyssale API

## Telnyx Storage
- `adgen-brand` bucket: curated image library
- `adgen-output` bucket: generated assets + metadata JSONs

## Telnyx Embeddings

For semantic search over the asset library and creative history:
```bash
curl -s -X POST "https://api.telnyx.com/v2/ai/embeddings" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "thenlper/gte-large", "input": "search query"}'
```
Models: `thenlper/gte-large`, `intfloat/multilingual-e5-large`
Use for: asset search, finding similar creatives, tagging recommendations.

## Abyssale Templates (29 available)

**API Key:** `~/.secrets/abyssale`
**Catalog:** `brand/abyssale-templates.json`

### Key Templates by Use Case

| Use Case | Template | ID | Type |
|----------|----------|----|------|
| Display 300x250 | Display Single Image Ad 1 | 3902c53d | static |
| Display 300x600 | Display Ad 1 | 2c966e99 | static |
| Display 728x90 | Display ad horizontal 1 | 7323ba26 | static |
| LinkedIn Video | CIP - LinkedIn Video | 1d8e159b | animated |
| LinkedIn GIF | LinkedIn Organic GIF | 0fbafb13 | animated |
| Social (AI) | AI Glossary - Social | 7b8f744f | static |
| Blog Featured | RC Post Featured Image | d80699fc | static |
| Release Notes | Release Note | 2f3bd587 | static |
| Consumer Panel | Consumer Insight Panel | deb0ddd8 | static |
| OG Image | Global #s og:image | 2f5d9304 | static |
| Twitter Image | Global #s twitter:image | f89c0861 | static |
| X Release Notes | x-release-notes | 03bdef36 | animated |

### Generate via API
```bash
ABYSSALE_KEY=$(cat ~/.secrets/abyssale)
curl -X POST "https://api.abyssale.com/banner/generate-multi-format" \
  -H "x-api-key: $ABYSSALE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "<template_id>",
    "elements": {
      "headline": {"text": "Your Headline"},
      "image": {"image_url": "https://..."}
    }
  }'
```
