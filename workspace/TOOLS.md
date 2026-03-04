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
