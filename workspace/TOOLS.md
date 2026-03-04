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

**Endpoint:** `https://us-central-1.telnyxcloudstorage.com` (S3-compatible)
**API Key:** `~/.secrets/telnyx` (used as both access key and secret key)

### Buckets

| Bucket | Purpose |
|--------|---------|
| `adgen-brand` | Curated brand assets — logos, imagery, textures, product screenshots |
| `adgen-output` | Generated ad creatives, campaign outputs, metadata JSONs |

### storage.py — Upload / Download / List

Pipe JSON to stdin. Reads API key from `~/.secrets/telnyx` at runtime.

**Upload a brand asset:**
```bash
echo '{"action":"upload","bucket":"adgen-brand","local_path":"brand/imagery/product/portal-dashboard.png","remote_key":"imagery/product/portal-dashboard.png"}' | python3 scripts/storage.py
```

**Download a generated output:**
```bash
echo '{"action":"download","bucket":"adgen-output","remote_key":"healthcare-q2/linkedin.png","local_path":"output/downloaded.png"}' | python3 scripts/storage.py
```

**List objects with prefix:**
```bash
echo '{"action":"list","bucket":"adgen-brand","prefix":"imagery/"}' | python3 scripts/storage.py
```

**Environment overrides:**
- `TELNYX_API_KEY` — use instead of `~/.secrets/telnyx`
- `TELNYX_STORAGE_ENDPOINT` — override storage endpoint

## pipeline.py — Full Brief-to-Assets Pipeline

Orchestrates the complete workflow: hero generation → render → metadata → multi-format export.
Call this instead of individual scripts.

### Usage
```bash
echo '{
  "brief": {
    "headline": "Cut Patient Wait Times 40%",
    "subhead": "AI-native voice infrastructure for healthcare",
    "cta": "Talk to Sales",
    "persona": "cio_healthcare",
    "campaign": "healthcare-q2"
  },
  "template": "dark-hero-left",
  "accent_color": "#D4E510",
  "hero_image": "brand/imagery/product/portal-dashboard.png",
  "generate_hero": false,
  "formats": ["linkedin_1200x1200", "google_rectangle", "meta_1080x1080"],
  "variants": 1,
  "output_dir": "output/healthcare-q2"
}' | python3 scripts/pipeline.py
```

### Input Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `brief.headline` | string | **required** | Main headline text |
| `brief.subhead` | string | `""` | Supporting subhead |
| `brief.cta` | string | `""` | Call-to-action button text |
| `brief.persona` | string | `""` | Target persona tag |
| `brief.campaign` | string | `""` | Campaign identifier |
| `template` | string | rotates | Template name (or omit for auto-rotation with variants) |
| `accent_color` | string | `#D4E510` | Brand accent color hex |
| `hero_image` | string | `""` | Path to curated hero image |
| `generate_hero` | bool | `false` | Generate hero via AI instead |
| `hero_prompt` | string | `""` | Prompt for AI hero generation |
| `hero_provider` | string | `"dalle"` | `dalle` or `gemini` |
| `formats` | list | `["linkedin_1200x1200"]` | Output format names |
| `variants` | int | `1` | Number of color/template variants |
| `output_dir` | string | `"output/campaign"` | Output directory |
| `background` | string | `"#000000"` | Background color hex |

### Output
JSON manifest to stdout with all generated file paths, variant details, and timing.

### Variants
When `variants` > 1, the pipeline rotates through brand palette colors (`#00C26E`, `#D4E510`, `#FF6B9D`) and optionally templates. Each variant gets a subdirectory (`v1/`, `v2/`, etc.).

---

## save_to_library.py — Save Images to Brand Library

For saving uploaded images (e.g., from Slack) into the curated brand library.

### Usage
```bash
echo '{
  "source_path": "/tmp/uploaded-image.png",
  "category": "product",
  "filename": "portal-dashboard-dark.png",
  "tags": ["portal", "dashboard", "dark", "professional"],
  "description": "Dark-themed portal dashboard screenshot"
}' | python3 scripts/save_to_library.py
```

### What it does
1. Validates image (PNG/JPG, minimum 2400px)
2. Copies to `brand/imagery/{category}/{filename}`
3. Updates `brand/imagery/index.md` with entry + tags
4. Uploads to Telnyx Storage (`adgen-brand` bucket)
5. Returns confirmation JSON

### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_path` | string | yes | Path to the source image |
| `category` | string | yes | Library category: `product`, `abstract`, `photography` |
| `filename` | string | yes | Target filename in library |
| `tags` | list | no | Tags for index.md searchability |
| `description` | string | no | Human-readable description |

---

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
