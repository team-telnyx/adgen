# Dark Hero Left

## When to Use
- Executive personas (CIO, VP, C-suite)
- ABM campaigns targeting decision-makers
- Authoritative, high-stakes tone
- Stat-driven headlines ("Cut Wait Times 40%")
- Enterprise product marketing

## Layout
- Background: solid black (#000000)
- Hero image: left 55% of canvas, full height, bleeds off left edge
- Headline: right side, upper third, cream text (#F5F0E8), bold, max 8 words
- Subhead: below headline, same x position, cream text at 70% opacity
- CTA: right side, lower third, pill button with accent color background and black text
- Logo: bottom-left corner, cream wordmark variant, 48px clearspace from edges

## Render Params

```json
{
  "template": "dark-hero-left",
  "background": "#000000",
  "hero_zone": {"x": 0, "y": 0, "w_pct": 55, "h_pct": 100, "bleed": true},
  "headline_zone": {"x_pct": 60, "y_pct": 20, "w_pct": 35, "color": "#F5F0E8", "font_weight": "bold", "font_size": 72},
  "subhead_zone": {"x_pct": 60, "y_pct": 45, "w_pct": 35, "color": "#F5F0E8", "opacity": 0.7, "font_size": 36},
  "cta_zone": {"x_pct": 60, "y_pct": 75, "style": "pill", "bg_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "bottom-left", "variant": "wordmark-cream", "clearspace": 48}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — use all elements as described above
- **linkedin_carousel (1080×1080):** Slightly reduce hero to 50%, increase headline font to 76px
- **google_rectangle (300×250):** Hide subhead, headline max 5 words, increase font weight, hero shrinks to 45%
- **google_leaderboard (728×90):** Headline + CTA only, no hero image, horizontal layout with logo far-right
- **google_skyscraper (160×600):** Vertical stack — icon logo top, headline split across 2-3 lines in center, CTA at bottom, no hero image
- **reddit_feed (1080×1350):** Hero fills left 50%, more vertical space for subhead
- **twitter_single (1200×675):** Hero left 45%, headline + CTA right, hide subhead
- **meta_feed (1080×1080):** Same as master layout
- **meta_stories (1080×1920):** Hero fills top 60% full-width, text block in bottom 40% on black background

## Supported Formats

| Format | Size | Platform |
|--------|------|----------|
| linkedin_1200x1200 | 1200×1200 | LinkedIn feed |
| linkedin_1200x627 | 1200×627 | LinkedIn landscape |
| meta_1080x1080 | 1080×1080 | Meta feed |
| meta_stories | 1080×1920 | Meta/IG stories |
| google_rectangle | 300×250 | Google Display |
| google_leaderboard | 728×90 | Google Display |
| google_skyscraper | 160×600 | Google Display |
| reddit_1080x1350 | 1080×1350 | Reddit feed |
| x_1600x900 | 1600×900 | X/Twitter |
