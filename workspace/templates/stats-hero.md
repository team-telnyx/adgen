# Stats Hero

## When to Use
- Data-driven ads with a compelling proof point
- When you have a strong statistic ("40%", "99.999%", "2.3B+")
- Performance marketing, ROI-focused campaigns
- CIO/executive personas who respond to quantified value
- Healthcare, finance, or any vertical where numbers build trust

## Layout
- Background: solid black (#000000)
- Stat number: center-left, oversized (120-160px), accent color — this is the focal point
- Stat unit/context: immediately right of or below the number, cream text, smaller (e.g., "%" or "reduction")
- Headline: below the stat, cream text, bold, explains the stat in context
- Subhead: below headline, cream at 60% opacity, supporting detail
- CTA: lower third, centered or left-aligned, pill button
- Logo: bottom-left or bottom-right, cream variant, 48px clearspace
- No hero image — the stat IS the visual. Negative space lets the number breathe.

## Render Params

```json
{
  "template": "stats-hero",
  "background": "#000000",
  "stat_zone": {"x_pct": 10, "y_pct": 18, "w_pct": 80, "align": "left", "color": "accent", "font_weight": "bold", "font_size": 144},
  "stat_unit_zone": {"x_pct": 10, "y_pct": 42, "w_pct": 60, "color": "#F5F0E8", "font_size": 36, "opacity": 0.8},
  "headline_zone": {"x_pct": 10, "y_pct": 55, "w_pct": 70, "color": "#F5F0E8", "font_weight": "bold", "font_size": 48},
  "subhead_zone": {"x_pct": 10, "y_pct": 70, "w_pct": 65, "color": "#F5F0E8", "opacity": 0.6, "font_size": 28},
  "cta_zone": {"x_pct": 10, "y_pct": 85, "style": "pill", "bg_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "bottom-right", "variant": "wordmark-cream", "clearspace": 48}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — stat dominates upper half, text in lower half
- **linkedin_carousel (1080×1080):** Same layout, stat at 130px
- **google_rectangle (300×250):** Stat number + headline only, hide subhead, stat at 80px, CTA compact
- **google_leaderboard (728×90):** Stat left (large), headline center, CTA right — single horizontal line
- **google_skyscraper (160×600):** Stat number at top (centered, 72px), headline middle, CTA bottom
- **reddit_feed (1080×1350):** More vertical breathing room — stat at 160px, push headline lower
- **twitter_single (1200×675):** Stat left 40%, headline + CTA right 55%
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Stat centered in upper third (180px), headline in center, CTA in lower quarter
