# AdGen Agent — Technical Spec

## The Product

This is not AI ad generation. This is **Slack-native creative production.**

```
@adgen
make a telecom ad
persona: CIO
theme: latency
```

A finished asset appears in the thread.

That workflow replaces:
- Marketing tickets
- Design iteration
- Slack threads asking for status
- Figma handoffs
- Revision cycles

The interface is the product. Everything below is plumbing.

## Design Principle

**No app. No codebase. Just an OpenClaw agent.**

AdGen is an agent workspace with brand assets, a render script, and Claude. That's it. No server, no database, no framework, no custom storage layer.

Claude makes decisions. One script makes pixels. Telnyx services handle storage and search. OpenClaw handles everything else.

## Architecture

```
Slack: "@adgen make a healthcare ad"
    ↓
OpenClaw Gateway → routes to AdGen agent
    ↓
Claude (creative director)
    ├── reads SOUL.md (brand rules, behavior)
    ├── reads MEMORY.md (what works for this persona)
    ├── reads brand/imagery/ (picks hero image)
    ├── reads templates/ (picks layout)
    ├── calls render.py via exec (passes JSON params → gets PNG back)
    ├── looks at the output (judges quality)
    ├── if not right → adjusts params → re-renders
    └── posts final asset to Slack thread
```

### What Claude Does
- Understands the brief
- Picks template, image, colors
- Judges output quality
- Handles revisions conversationally
- Updates memory with what worked

### What Code Does
- `render.py` — takes JSON params, outputs PNG. One script. No framework.

### What Telnyx Does
- Storage — asset library, generated outputs
- Embeddings — "show me best CIO ads" queries
- RAG — creative memory retrieval

### What OpenClaw Does
- Slack connectivity
- Agent lifecycle
- Memory (MEMORY.md)
- Cron (scheduled reports)
- Tool execution (exec, read, write)

## Agent Configuration

```json
{
  "id": "adgen",
  "name": "AdGen",
  "model": {
    "primary": "anthropic/claude-opus-4-6"
  },
  "identity": {
    "name": "AdGen",
    "emoji": "🎨"
  },
  "workspace": "~/.openclaw/agents/adgen/workspace"
}
```

### Channel Routing

```json
{
  "channels": {
    "slack": {
      "routes": [
        {
          "match": { "channel": ["C_CREATIVE_OPS"] },
          "agent": "adgen"
        }
      ]
    }
  }
}
```

## Workspace Structure

```
~/.openclaw/agents/adgen/workspace/
├── SOUL.md                        # Identity + brand rules + behavior
├── MEMORY.md                      # Learned creative preferences
├── TOOLS.md                       # How to use render.py
├── brand/
│   ├── rules.yaml                 # Brand rules (Claude reads these)
│   ├── colors.yaml                # Official palette
│   ├── logos/
│   │   ├── wordmark-cream.png
│   │   ├── wordmark-black.png
│   │   ├── icon-cream.png
│   │   └── icon-black.png
│   ├── fonts/
│   │   └── [brand typefaces]
│   └── imagery/
│       ├── index.md               # Browsable catalog with tags
│       ├── product/
│       │   ├── portal-dashboard.png
│       │   ├── api-docs-screen.png
│       │   └── mission-control.png
│       ├── photography/
│       │   ├── data-center-01.png
│       │   └── server-rack.png
│       └── abstract/
│           ├── network-pattern-dark.png
│           ├── gradient-green.png
│           └── geometric-citron.png
├── templates/
│   ├── dark-hero-left.md          # Markdown: description, zones, when to use
│   ├── light-minimal.md
│   ├── split-panel.md
│   ├── full-bleed-dark.md
│   ├── stats-hero.md
│   ├── gradient-accent.md
│   ├── testimonial.md
│   └── product-screenshot.md
├── scripts/
│   └── render.py                  # The only code. JSON in → PNG out.
└── output/                        # Local staging before storage upload
```

**That's the whole thing.** No src/, no tests/, no package.json, no requirements beyond Pillow.

## Brand Rules (brand/rules.yaml)

Claude reads this file. These aren't code — they're instructions Claude follows and checks against.

```yaml
colors:
  primary:
    black: "#000000"
    cream: "#F5F0E8"
  accent:
    green: "#00C26E"
    citron: "#D4E510"
    voice_ai_pink: "#FF6B9D"

typography:
  headline:
    max_words: 8
    weight: bold
  text_elements_max: 3
  mobile_first: true

logo:
  variants: [wordmark-cream, wordmark-black, icon-cream, icon-black]
  placement: [upper-left, lower-left]
  clearspace_px: 48
  selection:
    dark_background: cream
    light_background: black
    busy_area: icon_only
    clean_area: full_wordmark

layout:
  single_focal_point: true
  generous_negative_space: true
  hierarchy: headline → subhead → cta
```

## Templates (Markdown)

Each template is a Markdown file Claude reads to understand the layout. Not a schema consumed by code — instructions for Claude to translate into render params.

Example `templates/dark-hero-left.md`:

```markdown
# Dark Hero Left

## When to use
- Executive personas (CIO, VP, C-suite)
- ABM campaigns
- Authoritative tone
- Stat-driven headlines

## Layout
- Background: solid black or very dark
- Hero image: left 55%, full height, bleeds off edge
- Headline: right side, upper third, cream text, bold
- Subhead: below headline, 70% opacity
- CTA: right side, lower third, pill button (accent color bg, black text)
- Logo: bottom-left, cream variant, 48px clearspace

## Render params
template: dark-hero-left
background: "#000000"
hero_zone: {x: 0, y: 0, w: 55%, h: 100%, bleed: true}
headline_zone: {x: 60%, y: 20%, w: 35%}
subhead_zone: {x: 60%, y: 45%, w: 35%, opacity: 0.7}
cta_zone: {x: 60%, y: 75%, style: pill}
logo_zone: {position: bottom-left, variant: cream}

## Format adjustments
- google_300x250: hide subhead, headline max 5 words
- google_728x90: headline + CTA only, no hero image
- google_160x600: vertical, icon logo, headline stacked
```

Claude reads this, understands it, and passes the right params to render.py. If a new template is needed, write a Markdown file. No code changes.

## render.py

The only code in the system. A single script.

**Input:** JSON params via stdin or file
```json
{
  "template": "dark-hero-left",
  "format": "linkedin_1200x1200",
  "background": "#000000",
  "headline": "Cut Patient Wait Times 40%",
  "subhead": "AI-native voice infrastructure",
  "cta": "Talk to Sales",
  "accent_color": "#D4E510",
  "hero_image": "brand/imagery/product/portal-dashboard.png",
  "logo_variant": "wordmark-cream",
  "output": "output/healthcare-q2/linkedin_1200x1200.png"
}
```

**Output:** PNG file at the specified path.

**What it does:**
1. Creates canvas at master dimensions (1200×1200)
2. Fills background
3. Places + crops hero image in hero zone
4. Renders headline, subhead, CTA with exact font/size/position
5. Composites logo with clearspace
6. Saves master PNG

render.py only produces the master size. Multi-format export is handled by Abyssale (see below).

**What it doesn't do:**
- No multi-format rendering (Abyssale does that)
- No brand checking (Claude does that by looking at the output)
- No template selection (Claude does that)
- No image selection (Claude does that)
- No AI anything (it's deterministic)

**Dependencies:** Pillow + OpenAI SDK (for DALL-E) + Nano Banana skill (for Gemini image gen) + Abyssale API (for multi-format export).

**How Claude calls it:**
```bash
echo '{"template": "dark-hero-left", ...}' | python3 scripts/render.py
```

## Multi-Format Export via Abyssale

render.py produces one master design (1200×1200). Abyssale handles the format explosion.

**Why Abyssale, not render.py for every format:**
- Smart text reflow across wildly different aspect ratios (1200×1200 → 728×90 → 160×600)
- Knows what to hide vs shrink vs reposition per format
- Handles edge cases (leaderboard where headline barely fits)
- render.py stays simple — one master size, not 9 format variants

**Flow:**
```
render.py → master 1200×1200 PNG
    ↓
Claude calls Abyssale API with:
  - master image
  - text content (headline, subhead, CTA)
  - brand assets (logo, colors)
  - target formats list
    ↓
Abyssale returns all format variants
    ↓
Claude reviews each, uploads to Telnyx Storage
```

**Abyssale templates:** Pre-configured per format with Telnyx brand elements. Each template maps to an ad format with correct zones, text sizing, and element visibility rules.

**Supported formats:**

| Format | Dimensions | Notes |
|--------|-----------|-------|
| LinkedIn Single Image | 1200×1200 | Master size (from render.py) |
| LinkedIn Carousel | 1080×1080 | Per-card |
| Google Display Rectangle | 300×250 | Compact, may hide subhead |
| Google Display Leaderboard | 728×90 | Headline + CTA only |
| Google Display Skyscraper | 160×600 | Vertical, icon logo |
| Reddit Feed | 1080×1350 | Tall, more hero space |
| Twitter/X Single | 1200×675 | Wide, landscape |
| Meta Feed | 1080×1080 | Square |
| Meta Stories | 1080×1920 | Full vertical |

## Image Strategy

**Curated library (~50%)**
- Product screenshots, brand photography, proven assets
- Live in `brand/imagery/` with `index.md` describing each image with tags
- Claude browses the catalog, picks the best match
- Best for: anything that needs to look real (products, people, offices, data centers)

**Generated via DALL-E / Nano Banana (~35%)**
- Abstract, conceptual, atmospheric, textures, backgrounds
- Network visualizations, data flow imagery, connectivity concepts
- Mood/texture layers behind text
- Claude generates on the fly via exec — no pre-curation needed
- Solves the library bottleneck: instead of waiting for curated assets, generate what fits the brief in seconds
- **Rule: never generate faces, real products, or anything that needs to look photographic**
- Both providers available — Claude picks based on what works for the style:
  - **DALL-E** — stronger photorealistic textures, lighting
  - **Nano Banana Pro** — good for abstract/conceptual, fast

**Composited graphics (~15%)**
- Stats callouts ("40%"), data visualizations, icon layouts
- render.py handles these — big number + accent color, no hero image needed

## Adding Images to the Library

The image library is only as good as what's in it. Marketing team needs a dead-simple way to add images.

### Method 1: Slack (Recommended)

Drop an image in the creative ops channel and tell AdGen to save it:

```
[uploads image]
@adgen save this as a product screenshot, tags: portal, dashboard, dark background
```

AdGen:
1. Downloads the image from Slack
2. Saves to `brand/imagery/product/` with a descriptive filename
3. Adds entry to `index.md` with tags
4. Uploads to Telnyx Storage (`adgen-brand` bucket)
5. Confirms in thread

```
Saved: brand/imagery/product/portal-dashboard-dark.png
Tags: product, portal, dashboard, dark
```

That's it. No file system access needed. No PRs. No tooling.

### Method 2: Batch Upload

For bulk additions (e.g., after a brand shoot or product update):

```
@adgen I'm uploading a batch of new product screenshots
[uploads 10 images]
These are all product screenshots from the March 2026 portal redesign
```

AdGen processes each one, generates descriptive filenames and tags, adds all to the library.

### Image Requirements

When uploading, images should be:

| Requirement | Why |
|---|---|
| **PNG or high-quality JPG** | Compression artifacts ruin ad output |
| **Minimum 2400px on longest edge** | Needs to scale to largest format (1200×1200 @2x) |
| **No text baked in** | render.py handles all text — text in images can't be changed |
| **No logos baked in** | Logo compositing is automatic — baked logos double up |
| **Clean edges** | Bleed/crop zones need clean image edges |
| **Transparent background (PNG) when possible** | Easier compositing over colored backgrounds |

### Tagging Convention

Tags help Claude find the right image. Use these categories:

```
Type:     product, photography, abstract, icon, data-viz
Subject:  portal, api, network, server, team, office, data-center
Tone:     professional, technical, warm, bold, minimal
Color:    dark, light, green, citron, neutral
Persona:  cio, developer, devops, marketing, executive
```

Example: `product, portal, dashboard, dark, professional, cio`

Claude uses these tags to match images to briefs. Better tags = better image selection.

### Removing or Replacing Images

```
@adgen remove portal-old.png from the library
@adgen replace data-center.png with this updated version [uploads image]
```

### Library Health Check

```
@adgen how's the image library looking?
```

AdGen reports:
- Total images by category
- Categories with <3 images (gaps)
- Most/least used images
- Images that have never been used

## How Claude Checks Quality

No brand-gate code. Claude reads `brand/rules.yaml`, looks at the rendered output (via image tool), and checks:

- Does the headline exceed 8 words?
- Is there more than one focal point?
- Is the logo in an allowed position with clearspace?
- Are only brand colors used?
- Does it look right?

That last one matters. Claude's visual judgment on "does this ad look professional" is better than pixel-counting code. If something's off, Claude adjusts the params and re-renders.

## Future: Nice-to-Haves (End of Build)

These three features make the system significantly more powerful. All built within the OpenClaw paradigm — no custom databases, no frameworks, just agent primitives.

### 1. Creative Memory

Store what works per persona so the system gets smarter over time.

**How it works:** Just MEMORY.md. Claude updates it after campaigns with observed patterns.

```markdown
## Creative Patterns

### CIO Healthcare
- Template: dark-hero-left performs best
- Accent: citron > green on LinkedIn (15% higher CTR)
- Imagery: product screenshots > abstract
- Headlines: stat-driven ("40% reduction") outperforms benefit-driven

### Developer API
- Template: light-minimal
- Imagery: product screenshots (API docs, code)
- Headlines: direct and technical, no marketing speak
```

No custom system. Claude reads MEMORY.md on every brief and starts with proven defaults. When performance data comes back, Claude updates the patterns.

Over time this becomes automated creative optimization — the agent learns that `CIO → dark hero + stat headline + minimal CTA` without anyone coding that rule.

### 2. Variant Engine

Instead of generating one ad, generate six. Turns the system into an A/B testing machine.

```
User: @adgen give me 6 variants for the healthcare CIO campaign

Claude:
  - reads MEMORY.md for what works
  - picks 2 headlines × 2 templates × 2 accent colors
  - calls render.py 6 times with different params
  - posts all 6 in thread, labeled
  - asks which to export to all formats
```

No batch system. No variant framework. Claude just calls render.py multiple times with different params. The conversation is the interface for selecting winners.

### 3. Asset Graph

Make past assets queryable. "Show me ads we used for telecom latency campaigns."

**How it works:** Metadata JSON alongside each asset in Telnyx Storage. No custom database.

```json
{
  "campaign": "healthcare-q2",
  "persona": "cio_healthcare",
  "template": "dark-hero-left",
  "headline": "Cut Patient Wait Times 40%",
  "accent_color": "citron",
  "imagery_source": "tier_1_curated",
  "created": "2026-03-04T20:30:00Z",
  "performance": {}
}
```

Queries → Telnyx Embeddings search over metadata JSONs. Claude reads results and summarizes. No custom code, no search engine — just Storage + Embeddings, which are already Telnyx services.

When performance data comes back (CTR, conversions), Claude updates the metadata and MEMORY.md. The asset graph and creative memory feed each other.

### The Flywheel (When All Three Are Live)

```
Creative Memory learns patterns
    ↓
Variant Engine tests hypotheses
    ↓
Asset Graph stores results + performance
    ↓
Creative Memory updates with real data
    ↓
Next brief starts with proven defaults
```

Day 1: Claude picks templates based on heuristics. Month 3: Claude picks templates based on your actual performance data.

## Interaction Patterns

### New brief
```
User: @adgen LinkedIn ad for healthcare CIOs, dark, emphasize the 40% stat

AdGen: [reads brand rules, checks memory, picks template + image]
       [calls render.py]
       [posts image in thread]

       dark-hero-left / citron accent / portal screenshot
       Headline: "Cut Patient Wait Times 40%"
       
       Want other formats or revisions?
```

### Revision
```
User: lighter background, try green instead

AdGen: [adjusts params, re-renders]
       [posts revised image]

       Updated — cream background, green accent, switched to black logo.
```

### Multi-format
```
User: export all formats

AdGen: [sends master to Abyssale → gets all format variants back]
       [posts all in thread]
       [uploads to Telnyx Storage]

       9 formats exported to storage.
```

### Query past work
```
User: @adgen what CIO ads have we made?

AdGen: [searches Telnyx Embeddings over asset metadata]

       12 CIO ads across 3 campaigns:
       • healthcare-q2: 4 ads (best CTR: dark-hero-left + citron)
       • networking-launch: 5 ads
       • ai-platform: 3 ads
```

## What's NOT Here

- No server
- No database
- No API endpoints
- No Docker/Kubernetes
- No test suite (it's one script)
- No CI/CD pipeline
- No package management beyond `pip install Pillow`
- No framework
- No custom storage layer
- No custom search engine
- No brand-checking code

All of that is either Claude's judgment, OpenClaw primitives, or Telnyx services.

## Implementation Plan

Parallel agent spawn. Coldshot on render.py, Paperclip on workspace/brand assets, Sapper on templates + docs. Full system operational in days, not weeks.

### Day 1: Foundation (parallel)
- [ ] Register AdGen as OpenClaw agent with channel routing
- [ ] **Coldshot:** Build render.py (Pillow — JSON in, master PNG out, all template layouts)
- [ ] **Paperclip:** Write SOUL.md, TOOLS.md, brand/rules.yaml, brand/colors.yaml
- [ ] **Sapper:** Write all 8 template Markdown files
- [ ] **Sapper:** Curate initial image library (15+ assets) with index.md
- [ ] End-to-end test: brief in Slack → asset in thread

### Day 2: Full pipeline
- [ ] Telnyx Storage buckets (adgen-brand, adgen-output)
- [ ] Slack image upload → library flow working
- [ ] DALL-E + Nano Banana integration for generated imagery
- [ ] Asset metadata JSONs on every output
- [ ] Variant generation (multiple renders per brief)

### Day 3: Intelligence + polish
- [ ] Telnyx Embeddings over asset metadata for graph queries
- [ ] Creative memory seeded in MEMORY.md
- [ ] Library health check tool
- [ ] All interaction patterns tested (new brief, revision, multi-format, batch variants, query past work)
- [ ] Hand off to marketing team for real usage

## Success Criteria

- Brief to first asset: < 2 minutes
- Brand compliance: 100% (Claude checks every output)
- Revision turnaround: < 30 seconds
- Workspace total code: < 500 lines (render.py only)
- No infrastructure to maintain beyond the agent workspace
- Works entirely through Slack conversation
