# Telnyx Brand Guide — Quick Reference

A scannable summary of the brand rules AdGen enforces on every asset.

---

## Colors

| Color | Hex | When to Use |
|-------|-----|-------------|
| **Black** | `#000000` | Primary backgrounds (dark theme), text on light backgrounds. 60%+ of dark layouts. |
| **Cream** | `#F5F0E8` | Primary backgrounds (light theme), text on dark backgrounds. 60%+ of light layouts. |
| **Green** | `#00C26E` | CTAs, buttons, success states, accent lines. Use sparingly (10–15% of layout). |
| **Citron** | `#D4E510` | Stat callouts, data highlights, high-energy campaigns. 10–15% of layout. Higher CTR on LinkedIn for CIO personas. |
| **Voice AI Pink** | `#FF6B9D` | Voice AI product campaigns only. Do not use for general telecom creative. |
| **Dark Gray** | `#1A1A1A` | Subtle variation from pure black — card backgrounds, secondary panels. |
| **Mid Gray** | `#666666` | Subhead text, metadata, secondary information. |
| **Light Gray** | `#E5E0D8` | Subtle variation from cream — dividers, section breaks. |

### Proven Combinations
- **Dark + Citron:** Black bg, cream text, citron accent → Maximum readability, stat-driven ads
- **Light + Green:** Cream bg, black text, green accent → Clean, professional, developer-friendly
- **Core Brand:** Black bg, cream text, green accent → Standard Telnyx identity
- **Voice AI:** Black bg, cream text, pink accent → Voice AI campaigns only

All text-on-background combos must meet **WCAG AA** contrast (4.5:1 minimum). Cream on black = 18.1:1 — exceeds AAA.

---

## Fonts

| Use | Font | Weight | Notes |
|-----|------|--------|-------|
| **Headlines** | PP Formula | Extrabold | All hero text, display type. Max 8 words. |
| **Subheads** | Inter | Medium | Supporting text, 70% opacity on dark backgrounds. Max 15 words. |
| **Body copy** | Inter | Regular–Bold | CTAs, descriptions, metadata. |
| **CTA buttons** | Inter | Bold | Pill button style. Max 4 words. |

**Hard rule:** Never substitute with system fonts. PP Formula and Inter are the only approved typefaces.

---

## Logo Usage

### Variants
| Variant | Use On |
|---------|--------|
| **Wordmark (cream)** | Dark backgrounds, clean areas |
| **Wordmark (black)** | Light/cream backgrounds, clean areas |
| **Icon only (cream)** | Dark backgrounds, busy/tight areas |
| **Icon only (black)** | Light backgrounds, busy/tight areas |

### Placement Rules
- **Position:** Upper-left or lower-left only
- **Clearspace:** Minimum 48px on all sides
- **Never** place over busy or detailed image regions
- Use icon-only variant when space is tight

---

## Image Style

### On-Brand ✅
- Abstract visualizations (networks, data flows, connections)
- Dark backgrounds with accent color highlights
- Clean geometric compositions
- Product/tech imagery (servers, APIs, code)
- Transparent PNGs for compositing
- Minimum 2400px resolution

### Off-Brand ❌
- Real human faces (generated or stock)
- Text baked into hero images
- Logos baked into hero images
- Busy or cluttered compositions
- Stock photo clichés (handshakes, headsets, globe graphics)
- Low-resolution or pixelated imagery

### Image Sources
- **DALL-E:** Photorealistic scenes, product environments
- **Gemini:** Abstract, artistic, geometric visualizations
- **Asset library:** Previously saved brand imagery

---

## Copy Rules

- **Headline:** Max 8 words. Sentence case. Stat-driven beats vague.
- **Subhead:** Max 15 words. Supports the headline, doesn't repeat it.
- **CTA:** Max 4 words. Action-oriented ("Get Started," "See Pricing").
- **Total text elements:** Max 3 visible per asset (headline + subhead + CTA).
- **Dev audience:** No marketing buzzwords. Be specific and technical. "99.999% uptime" beats "industry-leading reliability."
- **Executive audience:** Lead with business outcomes and numbers. "Cut costs 40%" beats "optimize your infrastructure."

---

## Format Specs

### Static Ad Sizes

| Platform | Dimensions | Aspect Ratio |
|----------|-----------|--------------|
| LinkedIn (square) | 1200×1200 | 1:1 |
| LinkedIn (landscape) | 1200×627 | ~1.91:1 |
| Google Display (medium rectangle) | 300×250 | 6:5 |
| Google Display (leaderboard) | 728×90 | ~8:1 |
| Google Display (skyscraper) | 160×600 | ~1:3.75 |
| Google Display (large rectangle) | 336×280 | 6:5 |
| Meta (square) | 1080×1080 | 1:1 |
| Meta (landscape) | 1200×628 | ~1.91:1 |
| X / Twitter (landscape) | 1200×675 | 16:9 |
| X / Twitter (square) | 1080×1080 | 1:1 |
| Reddit (portrait) | 1080×1350 | 4:5 |
| Reddit (landscape) | 1200×628 | ~1.91:1 |

### Video Specs

| Aspect Ratio | Use Case |
|-------------|----------|
| 16:9 (landscape) | LinkedIn video, YouTube, web |
| 1:1 (square) | Social feeds, LinkedIn |
| 9:16 (vertical) | Stories, Reels, TikTok |

### Video Compositions (Remotion)
- **ProductLaunch** — New product/feature announcements
- **SocialAd** — General social media ad format
- **StatReveal** — Animated statistics and data points
- **FeatureDemo** — Product feature walkthrough

---

*Last updated: March 2026. Source of truth: `brand/rules.yaml` and `brand/colors.yaml`.*
