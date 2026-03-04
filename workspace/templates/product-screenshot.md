# Product Screenshot

## When to Use
- Product marketing and feature launches
- When you have a clear, compelling product screenshot
- Developer-facing ads showing the actual product (portal, API docs, dashboards)
- Mid-funnel content where showing the product drives interest
- Best when the screenshot tells the story — minimal text needed

## Layout
- Background: solid black (#000000) or dark gray (#1A1A1A)
- Product screenshot: center of canvas, occupying 60-70% of area, with subtle drop shadow or frame
- Screenshot may have rounded corners (8px radius) for a polished look
- Headline: above the screenshot, cream text (#F5F0E8), bold, concise (max 6 words)
- CTA: below the screenshot, pill button with accent color background
- Logo: upper-left, cream variant, 48px clearspace
- No subhead — the screenshot IS the supporting context
- Generous padding around screenshot (min 5% on each side)

## Render Params

```json
{
  "template": "product-screenshot",
  "background": "#000000",
  "headline_zone": {"x_pct": 15, "y_pct": 5, "w_pct": 70, "align": "center", "color": "#F5F0E8", "font_weight": "bold", "font_size": 52},
  "screenshot_zone": {"x_pct": 10, "y_pct": 18, "w_pct": 80, "h_pct": 60, "object_fit": "contain", "border_radius": 8, "shadow": {"enabled": true, "offset_y": 8, "blur": 24, "color": "rgba(0,0,0,0.5)"}},
  "cta_zone": {"x_pct": 35, "y_pct": 85, "w_pct": 30, "style": "pill", "bg_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "upper-left", "variant": "wordmark-cream", "clearspace": 48}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — screenshot centered with headline above and CTA below
- **linkedin_carousel (1080×1080):** Same layout, screenshot at 65% canvas area
- **google_rectangle (300×250):** Screenshot fills 70% of canvas (top portion), headline overlaid at top, CTA at bottom — very tight
- **google_leaderboard (728×90):** Small screenshot left (30%), headline + CTA right — screenshot acts as thumbnail
- **google_skyscraper (160×600):** Screenshot in upper 45% (full width, small), headline below, CTA at bottom
- **reddit_feed (1080×1350):** Screenshot can be larger (70% height), headline above, CTA anchored at bottom
- **twitter_single (1200×675):** Screenshot center (55% width), headline above, CTA below
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Screenshot in center 50% of canvas, headline at 10%, CTA at 85%

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
