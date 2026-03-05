# AdGen — Team Onboarding Guide

AdGen is Telnyx's Slack-native creative production agent. Give it a brief, get production-ready ads — static or video, any format, always on-brand.

---

## How to Access

1. Go to **#creative-ops** in Slack
2. Tag **@AdGen** with your brief
3. Assets appear in-thread, usually within 60 seconds

AdGen also works in DMs for quick one-off requests.

---

## Brief Format

Every brief needs at minimum: **what** you want and **who** it's for. The more context you give, the better the output.

### Example 1: Simple
```
@AdGen LinkedIn ad, headline: "99.999% Uptime, Zero Excuses", persona: IT directors
```

### Example 2: Detailed
```
@AdGen
- Format: LinkedIn + Google Display + Reddit
- Headline: "Cut Wait Times 40% with AI Voice"
- Persona: Healthcare CIOs
- Campaign: AI Voice Infrastructure Q1
- Style: Dark background, citron accent
- Image: Abstract network/voice visualization
```

### Example 3: Video
```
@AdGen
- Format: Video (LinkedIn + social)
- Headline: "One API. Global Coverage."
- Persona: Developers
- Style: ProductLaunch composition, dark theme
- Stats to animate: 70+ countries, <50ms latency, 99.999% uptime
```

---

## Output Types

| Type | What It Is | When to Use |
|------|-----------|-------------|
| **Static ads** | PNG images rendered via Abyssale templates | LinkedIn, Google Display, social posts, Reddit |
| **Video ads** | Motion graphics via Remotion | LinkedIn video, social video, product launches |
| **Clip assembly** | Cut/splice existing footage with overlays | Event recaps, testimonial edits, demo clips |

---

## Supported Formats

| Platform | Static Sizes | Video Sizes |
|----------|-------------|-------------|
| **LinkedIn** | 1200×1200, 1200×627 | 16:9, 1:1 |
| **Google Display** | 300×250, 728×90, 160×600, 336×280 | — |
| **Meta (Facebook/Instagram)** | 1080×1080, 1200×628 | 16:9, 1:1, 9:16 |
| **X (Twitter)** | 1200×675, 1080×1080 | 16:9, 1:1 |
| **Reddit** | 1080×1350, 1200×628 | — |

If you need a size not listed, just ask — AdGen can render any custom dimensions.

---

## Adding to the Asset Library

Have an image you want AdGen to remember for future use? Drop it in the thread and say:

```
@AdGen save this as "healthcare-abstract-01" for the healthcare campaign
```

AdGen will store it and use it when matching future briefs.

---

## Tips for Better Results

1. **Be specific about the persona.** "Developers" and "CIOs" get very different creative. AdGen adjusts template, tone, and color emphasis based on who's seeing the ad.

2. **Include a stat when you can.** "Cut costs 40%" outperforms "reduce your costs" in every format. Numbers stop scrolls.

3. **Specify dark or light theme.** Dark backgrounds perform better for developer audiences. Light/cream works better for executive/enterprise personas. AdGen will pick if you don't, but you know your campaign best.

4. **Request multiple formats upfront.** Say "LinkedIn + Google Display + Reddit" in one brief rather than three separate requests. AdGen renders all sizes in one pass.

5. **Mention the campaign name.** AdGen tracks what works per campaign. Saying "Q1 AI Voice campaign" lets it pull patterns from previous successful assets in that campaign.

6. **Give image direction.** "Abstract network visualization" or "dark gradient with green accent lines" gives AdGen a much better starting point than letting it guess.

---

## FAQ

**How long does it take?**
Static ads: ~30–60 seconds. Video: ~2–3 minutes. Clip assembly depends on footage length.

**Can I iterate?**
Yes. Reply in the same thread with what you want changed. "Swap to citron accent" or "try a lighter background" — AdGen iterates without starting over.

**What if I need a specific Abyssale template?**
Ask for it by name if you know it. Otherwise, describe what you want and AdGen picks the best match. You can always say "try template X instead" if you disagree.

**Can AdGen write copy for me?**
AdGen works with headlines and short supporting copy, not long-form. Bring your headline and AdGen handles the rest. If your headline is too long (8+ words), AdGen will suggest a tighter version.

**What if the output looks wrong?**
Tell AdGen in-thread what's off. Be specific: "headline is too small," "wrong logo variant," "background clashes with the accent." The more precise, the faster the fix.

**Can I get assets without a hero image?**
No — AdGen always generates a hero image. This is a brand rule. Every ad needs a strong visual, not just text on a color block.

**Who approves the final assets?**
You do. AdGen produces, humans approve. Nothing goes to media buying without your sign-off.

**Does it work outside #creative-ops?**
Yes, AdGen responds in any channel it's added to, plus DMs. But #creative-ops is the main hub where the team can see and build on each other's briefs.
