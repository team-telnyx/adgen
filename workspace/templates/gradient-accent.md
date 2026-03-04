# Gradient Accent

## When to Use
- Announcements, event promotion, product launches
- When no hero image is available or needed
- Clean, modern aesthetic — gradient IS the visual
- Works well for webinar promos, conference ads, date-driven campaigns
- Any persona — tone comes from copy, not imagery

## Layout
- Background: diagonal or vertical gradient from black (#000000) to accent color (e.g., #00C26E or #D4E510)
- Headline: centered, upper-center, cream text (#F5F0E8), bold — positioned on the darker portion of gradient
- Subhead: centered below headline, cream at 70% opacity
- CTA: centered, lower third, pill button — white/cream background with black text (contrast against gradient)
- Logo: upper-left, cream wordmark variant, 48px clearspace
- No hero image — the gradient background carries the visual weight
- Optional: date or event detail line above or below headline in accent color

## Render Params

```json
{
  "template": "gradient-accent",
  "background": {"type": "gradient", "direction": "diagonal_bottom_right", "stops": [{"position": 0, "color": "#000000"}, {"position": 100, "color": "accent"}]},
  "headline_zone": {"x_pct": 15, "y_pct": 28, "w_pct": 70, "align": "center", "color": "#F5F0E8", "font_weight": "bold", "font_size": 68},
  "subhead_zone": {"x_pct": 20, "y_pct": 50, "w_pct": 60, "align": "center", "color": "#F5F0E8", "opacity": 0.7, "font_size": 32},
  "cta_zone": {"x_pct": 30, "y_pct": 72, "w_pct": 40, "style": "pill", "bg_color": "#F5F0E8", "text_color": "#000000"},
  "logo_zone": {"position": "upper-left", "variant": "wordmark-cream", "clearspace": 48},
  "event_detail_zone": {"enabled": false, "x_pct": 20, "y_pct": 22, "w_pct": 60, "align": "center", "color": "accent", "font_size": 24, "font_weight": "bold"}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — centered text on diagonal gradient, balanced negative space
- **linkedin_carousel (1080×1080):** Same layout, reduce fonts by 10%
- **google_rectangle (300×250):** Headline (max 5 words) + CTA only, gradient simplified to vertical
- **google_leaderboard (728×90):** Horizontal gradient (left-to-right), logo left, headline center, CTA right
- **google_skyscraper (160×600):** Vertical gradient (top-to-bottom), headline stacked in center, CTA bottom
- **reddit_feed (1080×1350):** Larger headline area, push CTA lower to 80%
- **twitter_single (1200×675):** Headline left-center, CTA right-center, gradient flows left-to-right
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Gradient flows top-to-bottom, headline centered at 35%, CTA at 70%
