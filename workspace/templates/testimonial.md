# Testimonial

## When to Use
- Customer quotes and social proof
- Case study promotion
- Trust-building for mid-funnel audiences
- When you have a strong, concise customer quote (1-2 sentences)
- Works especially well for enterprise personas who value peer validation

## Layout
- Background: solid black (#000000) or very dark
- Large quotation mark: upper-left area, oversized decorative element in accent color (120-160px), low opacity (0.3)
- Quote text: center of canvas, cream text (#F5F0E8), italic or regular weight, generous line height
- Attribution: below quote, accent color, bold — "— Name, Title, Company"
- Optional: small company logo or headshot to the left of attribution (circular crop, 64px)
- CTA: lower third, pill button with accent background
- Telnyx logo: bottom-left, cream variant, 48px clearspace
- Keep layout breathing — the quote is the focal point, everything else supports it

## Render Params

```json
{
  "template": "testimonial",
  "background": "#000000",
  "quote_mark_zone": {"x_pct": 8, "y_pct": 12, "character": "\u201C", "color": "accent", "font_size": 160, "opacity": 0.3},
  "quote_zone": {"x_pct": 12, "y_pct": 28, "w_pct": 76, "align": "left", "color": "#F5F0E8", "font_style": "italic", "font_size": 42, "line_height": 1.5},
  "attribution_zone": {"x_pct": 12, "y_pct": 65, "w_pct": 76, "color": "accent", "font_weight": "bold", "font_size": 24},
  "headshot_zone": {"enabled": false, "x_pct": 12, "y_pct": 62, "size_px": 64, "shape": "circle"},
  "cta_zone": {"x_pct": 12, "y_pct": 82, "style": "pill", "bg_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "bottom-left", "variant": "wordmark-cream", "clearspace": 48}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — quote centered with ample vertical spacing
- **linkedin_carousel (1080×1080):** Same layout, reduce quote font to 38px
- **google_rectangle (300×250):** Short quote only (max 10 words), hide attribution detail, small quotation mark
- **google_leaderboard (728×90):** Quote excerpt (max 8 words) + attribution on one line, no quotation mark decoration
- **google_skyscraper (160×600):** Quote stacked vertically across full width, attribution at bottom, CTA below
- **reddit_feed (1080×1350):** Larger quotation mark, more vertical space between quote and attribution
- **twitter_single (1200×675):** Quote left 60%, attribution + CTA right 35%
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Large quotation mark at 15%, quote in center 40%, attribution at 65%, CTA at 80%

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
