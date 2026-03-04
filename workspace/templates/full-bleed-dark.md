# Full Bleed Dark

## When to Use
- Awareness campaigns and bold brand statements
- When you have a striking hero image that should dominate
- High visual impact — photography-forward or cinematic feel
- Data center, infrastructure, or network imagery
- Top-of-funnel content where visual punch matters more than detail

## Layout
- Background: full-bleed hero image covering 100% of canvas
- Dark gradient overlay: bottom 50% fades from transparent to black (opacity 0.85)
- Headline: lower third, left-aligned, cream text (#F5F0E8), bold, large — sits on the gradient
- Subhead: below headline, cream text at 70% opacity
- CTA: below subhead, pill button with accent color background
- Logo: upper-left corner, cream icon or wordmark variant (choose based on image complexity), 48px clearspace
- The hero image IS the design — text is secondary, anchored on the gradient

## Render Params

```json
{
  "template": "full-bleed-dark",
  "hero_zone": {"x": 0, "y": 0, "w_pct": 100, "h_pct": 100, "object_fit": "cover"},
  "gradient_overlay": {"direction": "bottom", "start_opacity": 0.0, "end_opacity": 0.85, "start_pct": 40, "end_pct": 100, "color": "#000000"},
  "headline_zone": {"x_pct": 8, "y_pct": 65, "w_pct": 60, "color": "#F5F0E8", "font_weight": "bold", "font_size": 72},
  "subhead_zone": {"x_pct": 8, "y_pct": 78, "w_pct": 55, "color": "#F5F0E8", "opacity": 0.7, "font_size": 32},
  "cta_zone": {"x_pct": 8, "y_pct": 88, "style": "pill", "bg_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "upper-left", "variant": "icon-cream", "clearspace": 48}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — full-bleed image, gradient bottom half, text anchored low
- **linkedin_carousel (1080×1080):** Same layout, reduce headline to 64px
- **google_rectangle (300×250):** Gradient covers bottom 60%, headline only (max 5 words) + small CTA, icon logo
- **google_leaderboard (728×90):** Image fills full width, gradient covers right 60%, headline + CTA right-aligned
- **google_skyscraper (160×600):** Image fills top 55%, solid black bottom 45% with headline stacked + CTA
- **reddit_feed (1080×1350):** More vertical space — gradient starts at 50%, larger headline area
- **twitter_single (1200×675):** Gradient covers right 50%, headline + CTA right-aligned over gradient
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Image fills full canvas, gradient covers bottom 40%, text in bottom quarter

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
