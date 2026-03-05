# TOOLS.md — AdGen

## Pipeline Overview

The AdGen pipeline produces professional ad creatives from a brief:

```
Brief → AI Hero Image (DALL-E/Gemini) → Upload to Telnyx Storage → Abyssale renders final ad → Download → Metadata
```

**ONLY renderer:** Abyssale templates — professional output, proper typography, brand-consistent.
**NO Pillow fallback.** If a requested size doesn't match any Abyssale template format, output the closest available format instead. Never custom-render via render.py.

---

## pipeline.py — Full Brief-to-Assets Pipeline

The main orchestrator. Call this for all ad generation.

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
  "image_provider": "dalle",
  "image_prompt": "Abstract medical network visualization, dark background with green accent lighting, professional healthcare technology",
  "abyssale_template": "7b8f744f",
  "formats": ["facebook-featured"],
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
| `image_provider` | string | `"dalle"` | `dalle` or `gemini` |
| `image_prompt` | string | `""` | Prompt for AI hero image generation |
| `abyssale_template` | string | `""` | Abyssale template ID (full UUID or short ID) |
| `formats` | list | `["facebook-featured"]` | Abyssale format names from template |
| `output_dir` | string | `"output/campaign"` | Output directory |
| `background` | string | `"#000000"` | Background color (used in Pillow fallback) |

### Pipeline Steps
1. Generate hero image via DALL-E or Gemini (`generate_image.py`)
2. Upload hero to Telnyx Storage for public URL (`storage.py`)
3. Fetch Abyssale template details to discover elements
4. Smart-map brief fields → template elements (headline→title, subhead→subtitle, hero→image)
5. Call Abyssale generation API per format
6. Download generated images to output_dir
7. Create metadata sidecar per file (`asset_metadata.py`)
8. If Abyssale fails at any step → fall back to Pillow render.py

### Output
JSON manifest to stdout with all generated file paths, renderer used, timing.

---

## generate_image.py — AI Image Generation

Generates hero images via DALL-E 3 or Gemini.

### Usage
```bash
echo '{
  "prompt": "Abstract medical network, dark background, green accents",
  "provider": "dalle",
  "output": "output/hero.png",
  "size": "1024x1024",
  "style": "natural"
}' | python3 scripts/generate_image.py
```

| Provider | Best For |
|----------|----------|
| `dalle` | Photorealistic imagery, product visuals, industry scenes |
| `gemini` | Abstract/artistic, textures, conceptual backgrounds |

---

## abyssale_export.py — Abyssale Smart Export

Standalone Abyssale generation with auto-discovery. Can be used independently of the pipeline.

### Smart Mode (recommended)
```bash
echo '{
  "template_id": "7b8f744f-1faf-4b14-91ed-76a8e3028753",
  "brief": {
    "headline": "Your Headline",
    "subhead": "Supporting text",
    "cta": "Learn More"
  },
  "hero_url": "https://public-url-to-hero.png",
  "output_dir": "output/export/"
}' | python3 scripts/abyssale_export.py
```

Auto-discovers template elements, maps brief fields intelligently, generates all available formats.

### Direct Mode (legacy)
```bash
echo '{
  "template_id": "7b8f744f-1faf-4b14-91ed-76a8e3028753",
  "elements": {
    "proper_name": {"text": "AI Latency"},
    "tb-image_0": {"image_url": "https://..."}
  },
  "formats": ["facebook-featured"],
  "output_dir": "output/export/"
}' | python3 scripts/abyssale_export.py
```

---

## render.py — Pillow Render (Fallback Only)

Local PNG renderer using Pillow. **Used only when Abyssale is unavailable.**

### Usage
```bash
echo '{"template": "dark-hero-left", "format": "linkedin_1200x1200", ...}' | python3 scripts/render.py
```

### Templates
`dark-hero-left`, `light-minimal`, `split-panel`, `full-bleed-dark`, `stats-hero`, `gradient-accent`, `testimonial`, `product-screenshot`

### Formats
`linkedin_1200x1200`, `linkedin_carousel`, `google_rectangle`, `google_leaderboard`, `google_skyscraper`, `reddit_feed`, `twitter_single`, `meta_feed`, `meta_stories`

---

## Abyssale Templates

Template catalog at: `brand/abyssale-templates.json` (29 templates)

### Key Templates

| ID | Name | Type | Use Case |
|----|------|------|----------|
| `7b8f744f` | AI Glossary - Social | static | Social ads with image + text |
| `d80699fc` | RC Post Featured Image | static | Blog/article featured images |
| `3902c53d` | Display Single Image Ad 1 | static | Google Display 300×250 |
| `2c966e99` | Display Ad 1 | static | Google Display 300×600 |
| `7323ba26` | Display ad horizontal 1 | static | Google Leaderboard 728×90 |
| `1d8e159b` | CIP - LinkedIn Video | animated | LinkedIn video ads |
| `0fbafb13` | LinkedIn Organic GIF | animated | LinkedIn organic posts |

### Abyssale API Reference
- Template list: `GET https://api.abyssale.com/templates` (header: `x-api-key`)
- Template details: `GET https://api.abyssale.com/templates/{id}`
- Generate: `POST https://api.abyssale.com/banner-builder/{id}/generate`
  ```json
  {
    "template_format_name": "format-name",
    "elements": {
      "element_name": {"payload": "text value"},
      "element_name": {"image_url": "https://..."}
    }
  }
  ```

---

## Telnyx Storage

**Endpoint:** `https://us-central-1.telnyxcloudstorage.com` (S3-compatible)
**API Key:** `~/.secrets/telnyx` (used as both access key and secret key)

### Buckets

| Bucket | Purpose |
|--------|---------|
| `adgen-brand` | Curated brand assets + uploaded hero images for Abyssale |
| `adgen-output` | Generated ad creatives, campaign outputs |

### storage.py — Upload / Download / List

```bash
echo '{"action":"upload","bucket":"adgen-brand","local_path":"hero.png","remote_key":"heroes/hero.png"}' | python3 scripts/storage.py
echo '{"action":"download","bucket":"adgen-output","remote_key":"ad.png","local_path":"dl.png"}' | python3 scripts/storage.py
echo '{"action":"list","bucket":"adgen-brand","prefix":"heroes/"}' | python3 scripts/storage.py
```

---

## Brand Assets
- Rules: `brand/rules.yaml`
- Colors: `brand/colors.yaml`
- Logos: `brand/logos/`
- Imagery: `brand/imagery/` — browse `index.md`
- Abyssale templates: `brand/abyssale-templates.json`

## Telnyx Embeddings

For semantic search over assets:
```bash
curl -s -X POST "https://api.telnyx.com/v2/ai/embeddings" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "thenlper/gte-large", "input": "search query"}'
```

## CRITICAL: File Output Paths

**ALL generated files MUST be saved to `workspace/output/` (relative to workspace root).**
- NEVER save to `/tmp/` or any path outside the workspace
- Use relative paths from the workspace root

## Posting Images to Slack (CRITICAL)

**Use the Abyssale CDN URL with MEDIA: prefix:**
```
MEDIA:https://cdn.abyssale.com/ab1484a5-b4de-4542-bca3-c101f8bcb5eb/example.jpeg
```

**Rules:**
- ALWAYS use the `cdn_url` from Abyssale's API response with `MEDIA:` prefix
- These are public HTTPS URLs — they work everywhere
- Put each MEDIA: on its own line
- DO NOT use local file paths (output/..., ./output/...) — they fail due to path resolution
- If Abyssale CDN URL is unavailable, use the Telnyx Storage URL instead

## Video Generation

### render_video.py (Remotion)
```bash
echo '{"composition":"ProductLaunch","props":{"headline":"Cut Wait Times 40%","subhead":"AI-native voice","cta":"See Demo","accentColor":"#D4E510"},"format":"landscape","output":"output/video.mp4"}' | python3 scripts/render_video.py
```
Compositions: ProductLaunch, SocialAd, StatReveal, FeatureDemo
Formats: landscape (1920x1080), square (1080x1080), vertical (1080x1920)

### edit_video.py (Editly)
```bash
echo '{"operation":"assemble","clips":[{"path":"clip1.mp4"},{"path":"clip2.mp4"}],"output":"output/assembled.mp4"}' | python3 scripts/edit_video.py
```
