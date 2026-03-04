# Light Minimal

## When to Use
- Developer personas (engineers, DevOps, technical leads)
- Technical content, API launches, documentation announcements
- Subtle, understated tone — let the product speak
- Content that values clarity over visual impact
- Brands that want to feel approachable and modern

## Layout
- Background: cream (#F5F0E8) or off-white
- Headline: centered horizontally, upper-center of canvas, black text (#000000), bold
- Subhead: centered below headline, black text at 60% opacity, regular weight
- CTA: centered, lower third, text-link style or minimal pill button (accent border, no fill)
- Logo: upper-left, black wordmark variant, 48px clearspace
- No hero image — generous negative space is the design element
- Optional: thin accent-colored rule line between headline and subhead

## Render Params

```json
{
  "template": "light-minimal",
  "background": "#F5F0E8",
  "headline_zone": {"x_pct": 15, "y_pct": 30, "w_pct": 70, "align": "center", "color": "#000000", "font_weight": "bold", "font_size": 64},
  "subhead_zone": {"x_pct": 20, "y_pct": 50, "w_pct": 60, "align": "center", "color": "#000000", "opacity": 0.6, "font_size": 32},
  "cta_zone": {"x_pct": 35, "y_pct": 72, "w_pct": 30, "style": "outline_pill", "border_color": "accent", "text_color": "#000000"},
  "logo_zone": {"position": "upper-left", "variant": "wordmark-black", "clearspace": 48},
  "accent_rule": {"enabled": true, "y_pct": 46, "x_pct": 35, "w_pct": 30, "color": "accent", "thickness": 2}
}
```

## Format Adjustments
- **linkedin_single (1200×1200):** Master size — all elements centered with ample whitespace
- **linkedin_carousel (1080×1080):** Same layout, reduce font sizes by 10%
- **google_rectangle (300×250):** Headline only (max 5 words) + CTA, hide subhead and accent rule
- **google_leaderboard (728×90):** Logo left, headline center, CTA right — all on one horizontal line
- **google_skyscraper (160×600):** Icon logo top, headline stacked across lines in center, CTA at bottom
- **reddit_feed (1080×1350):** More vertical space — push headline to 25% from top, CTA to 80%
- **twitter_single (1200×675):** Headline left-aligned at 40%, CTA right side
- **meta_feed (1080×1080):** Same as master
- **meta_stories (1080×1920):** Headline in center third, large font (80px), CTA in lower quarter
