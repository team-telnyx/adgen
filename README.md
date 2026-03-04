# AdGen 🎨

Slack-native ad creative production powered by an OpenClaw agent. Type a brief, get a finished asset in the thread — no design tickets, no Figma handoffs, no revision cycles.

## How It Works

```
@adgen LinkedIn ad for healthcare CIOs, dark, emphasize the 40% stat
```

AdGen picks the right template, selects imagery, renders the asset, checks it against brand rules, and posts the result. Revisions happen in the thread:

```
@adgen lighter background, try green instead of citron
```

### Multi-Format Export

```
@adgen export all formats
```

Produces all 9 ad formats (LinkedIn, Google Display, Reddit, Twitter/X, Meta) via Abyssale.

### Adding Images

Drop an image in the creative ops channel:

```
[upload image]
@adgen save this as a product screenshot, tags: portal, dashboard, dark
```

AdGen saves it to the library, tags it, and it's immediately available for future briefs.

## Templates

| Template | Best For | Description |
|----------|----------|-------------|
| `dark-hero-left` | Executive/ABM campaigns | Hero image left 55%, headline right, black background |
| `light-minimal` | Developer/technical content | Clean cream background, centered text, no imagery |
| `split-panel` | Product comparisons | 50/50 vertical split — image one side, text the other |
| `full-bleed-dark` | Awareness campaigns | Full-bleed hero with dark gradient overlay |
| `stats-hero` | Data-driven proof points | Big stat number as focal point |
| `gradient-accent` | Announcements/events | Gradient background (black → accent), no hero image |
| `testimonial` | Customer social proof | Quote layout with attribution |
| `product-screenshot` | Feature launches | Product screenshot prominently displayed |

Template docs live in `workspace/templates/`. Each describes when to use it, the layout, render params, and format adjustments.

## Ad Formats

| Format | Dimensions | Use |
|--------|-----------|-----|
| LinkedIn Single Image | 1200×1200 | Master size |
| LinkedIn Carousel | 1080×1080 | Per-card |
| Google Display Rectangle | 300×250 | Sidebar/in-content |
| Google Display Leaderboard | 728×90 | Banner |
| Google Display Skyscraper | 160×600 | Side rail |
| Reddit Feed | 1080×1350 | In-feed |
| Twitter/X Single | 1200×675 | In-feed |
| Meta Feed | 1080×1080 | In-feed |
| Meta Stories | 1080×1920 | Full-screen vertical |

## Adding New Templates

Create a Markdown file in `workspace/templates/` with:

1. **When to Use** — persona, campaign type, tone
2. **Layout** — where each element goes, in plain English
3. **Render Params** — JSON params for render.py
4. **Format Adjustments** — what changes per ad format

No code changes needed. Claude reads the Markdown and translates it to render params.

## Architecture

- **Claude** — creative director (picks template, image, colors; judges output quality)
- **render.py** — the only code; takes JSON params, outputs PNG
- **Abyssale** — multi-format export from master design
- **Telnyx Storage** — asset library and generated outputs
- **OpenClaw** — agent lifecycle, Slack connectivity, memory

## Image Library

Browse `workspace/brand/imagery/index.md` for the full catalog with tags. Images are organized by type:

- `product/` — Screenshots, dashboards, UI
- `photography/` — Data centers, infrastructure, teams
- `abstract/` — Network patterns, gradients, geometric textures

See the index file for tagging conventions and image requirements.
