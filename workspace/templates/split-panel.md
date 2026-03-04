# Split Panel

## When to Use
- Product comparisons or before/after scenarios
- Feature highlights where visual proof matters
- When you have a strong product screenshot or hero image
- Balanced layouts where image and message carry equal weight
- Works across personas — adjust tone via copy, not layout

## Layout
- Background: split — left panel and right panel each occupy 50% of canvas width
- Image panel: one side (default left), full height, image fills the panel edge-to-edge
- Text panel: other side, solid background (black or cream depending on tone)
- Headline: text panel, upper third, bold, contrasting color to panel background
- Subhead: below headline, same panel, 70% opacity
- CTA: text panel, lower third, pill button
- Logo: bottom of text panel, appropriate variant for panel background color, 48px clearspace
- Thin vertical divider line in accent color between panels (optional)

## Render Params

```json
{
  "template": "split-panel",
  "image_side": "left",
  "image_zone": {"x_pct": 0, "y_pct": 0, "w_pct": 50, "h_pct": 100, "object_fit": "cover"},
  "text_panel": {"x_pct": 50, "y_pct": 0, "w_pct": 50, "h_pct": 100, "bg_color": "#000000"},
  "headline_zone": {"x_pct": 55, "y_pct": 25, "w_pct": 40, "color": "#F5F0E8", "font_weight": "bold", "font_size": 60},
  "subhead_zone": {"x_pct": 55, "y_pct": 48, "w_pct": 40, "color": "#F5F0E8", "opacity": 0.7, "font_size": 28},
  "cta_zone": {"x_pct": 55, "y_pct": 75, "style": "pill", "bg_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "bottom-right", "variant": "wordmark-cream", "clearspace": 48},
  "divider": {"enabled": false, "x_pct": 50, "color": "accent", "thickness": 3}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — true 50/50 split works well at this ratio
- **linkedin_carousel (1080×1080):** Same layout, slightly reduce text font sizes
- **google_rectangle (300×250):** Stack vertically — image top 50%, text bottom 50%, headline + CTA only
- **google_leaderboard (728×90):** No split — horizontal layout with small image left (30%), headline + CTA right
- **google_skyscraper (160×600):** Vertical split — image top 45%, text bottom 55%, headline stacked
- **reddit_feed (1080×1350):** Image panel 55% width, text panel 45% — more room for the visual
- **twitter_single (1200×675):** 45/55 split (image/text) — text needs more horizontal space at this ratio
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Horizontal split becomes vertical — image top 55%, text bottom 45%
