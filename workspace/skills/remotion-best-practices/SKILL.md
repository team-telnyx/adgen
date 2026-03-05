---
name: remotion-best-practices
description: Best practices for Remotion - Video creation in React
metadata:
  tags: remotion, video, react, animation, composition
---

## Design Quality Standards

### Resolution Standards
Always render at 1920x1080 (1080p) minimum. Never ship 720p.

| Format | Width | Height | Use case |
|--------|-------|--------|----------|
| 16:9 landscape | 1920 | 1080 | YouTube, website embeds, presentations |
| 9:16 vertical | 1080 | 1920 | Instagram Reels, TikTok, YouTube Shorts |
| 1:1 square | 1080 | 1080 | Instagram feed, LinkedIn |
| 4K landscape | 3840 | 2160 | High-end presentations (render time 4x) |

Default fps: 30. Use 60fps only when smooth motion is critical (scrolling UIs, fast transitions).

### Typography Standards
Telnyx uses two fonts in all video content:

- **PP Formula** - Branded heading font. Use for large headlines, stats, hook text, and CTAs.
- **Inter** - Body font. Use for descriptions, labels, muted text, and UI elements.

In `theme.ts`: `FONTS.heading` for PP Formula, `FONTS.sans` for Inter.

**Loading fonts in Remotion:**
```tsx
// In your composition's Root or a wrapper component:
import { staticFile } from "remotion";

const fontFace = `
@font-face {
  font-family: "PP Formula";
  src: url("${staticFile("fonts/PPFormula-Medium.otf")}") format("opentype");
  font-weight: 500;
}
`;
// Inject via <style> in an AbsoluteFill wrapper
```

Place font files in `public/fonts/` of your Remotion project. Inter is also available via `@remotion/google-fonts`.

### Narrative Arc for Video Structure
Every video should follow a clear narrative arc:

1. **Why Now** - Opening hook that establishes context or urgency (1-3 seconds)
2. **What Changes** - The core message or transformation being presented (main content)
3. **How It Works** - Demonstration or explanation of the mechanism (detail section)
4. **Next Steps** - Clear call to action or conclusion (final 3-5 seconds)

Structure timing accordingly: distribute content across the middle sections proportionally.

### One Idea Per Scene
Apply the "one idea per slide" principle to video scenes:

- Each composition or scene should communicate a single concept
- Avoid packing multiple distinct ideas into one frame
- If a scene has competing visual elements, consider splitting into separate scenes with transitions
- Use visual hierarchy to make the primary idea instantly clear

### Template-First Approach for Video Scenes
Don't design from scratch every time:

1. Start with proven composition templates for common patterns (title cards, content slides, feature reveals, testimonials)
2. Customize templates with brand colors, fonts, and specific content
3. Build a library of scene templates for your most frequently used patterns
4. Reuse scene structures across videos to maintain consistency

### Placeholder Over Invention
Never generate fake data, screenshots, or statistics:

- Use clear placeholder markers like `[PLACEHOLDER: your metric here]` for numbers
- Mark where product screenshots or visuals should be inserted
- For mockups, use generic placeholders rather than invented content
- Flag any generated statistics as placeholders in comments

### QA Checklist for Video Delivery
Before rendering or publishing any Remotion video, verify:

- **Timing**: Pacing feels appropriate, no scene drags or feels rushed
- **Transitions**: Smooth and purposeful, consistent style throughout
- **Text Readability**: Font sizes readable on target aspect ratio, sufficient contrast
- **Brand Consistency**: Colors, fonts, and logos match brand guidelines
- **Audio Balance**: Volume levels consistent, clear speech, no clipping
- **Responsive Elements**: Test on target aspect ratios (16:9, 9:16, 1:1)
- **Placeholder Cleanup**: No placeholder text remains in final render
- **Rendering Performance**: Compositions render efficiently without timeout issues

## AI-Assisted Workflow (Coding Agents + Remotion)

When building Remotion videos with AI coding agents (Claude, OpenCode, Cursor, etc.), follow these patterns for best results.

### Three Rules for AI + Remotion

1. **Explicitly reference the skill** - Tell the agent to "use the remotion-best-practices skill" or read specific rule files. Don't assume it picks up context automatically.

2. **One change at a time** - Don't ask for 5-10 changes in one message. Single requests = better results. "Add a fade-in to the title" not "add fade-in, change colors, adjust timing, and add a counter."

3. **Feed Remotion docs when needed** - For advanced features (audio visualization, captions, 3D), grab the relevant Remotion documentation. Add `.md` to any remotion.dev URL for a markdown version you can paste directly.

### Section-by-Section Building

Don't try to build the whole video at once. Build scene by scene:

```
1. Intro section (hook/title) → verify it works
2. Main content section → verify
3. Feature/demo section → verify  
4. CTA/outro section → verify
5. Then refine weak sections individually
```

This matches the "one idea per scene" principle and gives the agent focused context.

### Iteration Pattern

Follow this loop for each section:

1. **Basic first** - Get the structure working (black bg + white text is fine)
2. **Visual polish** - Add gradients, animations, brand colors
3. **Timing refinement** - Adjust animation timing, easing curves
4. **Advanced features** - Add audio reactivity, complex transitions, etc.

Expect to spend 10-15 minutes iterating on complex sections (like animated cards or product reveals).

### Documentation Feeding

When the agent doesn't know a Remotion API:

```bash
# Get markdown version of any Remotion doc page
https://remotion.dev/docs/audio-visualization
→ https://remotion.dev/docs/audio-visualization.md
```

Paste the markdown into chat. This is faster than the agent searching.

### Pre-Flight Checklist (Before Starting)

Before asking the agent to build a Remotion video:

1. **Check the clip manifest** - `the project public/ folder` for existing assets
2. **Check launchpad patterns** - `skills/remotion-best-practices/rules/launchpad-animations.md` for reusable motion components
3. **Check existing projects** - Similar work you can reference
4. **Prepare assets** - Drop logos, images into `public/` folder first

## Prompt Templates

Proven prompts from [remotion.dev/prompts](https://www.remotion.dev/prompts) that produce high-quality results:

### News Article Headline Highlight
**Source:** https://www.remotion.dev/prompts/news-article-headline-highlight
**Tool:** Claude Code (Opus 4.5)

Import a screenshot of a news article, use tesseract CLI for OCR to find text positions, then in Remotion:
- Load image on a white full HD background with generous padding
- Over 5 seconds, slowly zoom in with subtle 3D rotation (left to right, ~15deg per axis)
- Start with full blur, unblur over 1 second
- After unblur, evolve a rough.js highlighter left-to-right over target words
- Highlighter appears behind text (white background)
- Check for existing lockfiles before installing dependencies

**Key techniques:** OCR positioning, 3D transforms (perspective/rotateX/rotateY), blur animation, rough.js canvas overlay, z-index layering.

### Travel Route on Map with 3D Landmarks
**Source:** https://www.remotion.dev/prompts/travel-route-on-map-with-3d-landmarks
**Tool:** Claude Code (Opus 4.5)

Multi-step travel animation:
- Add a map composition, zoom out of LA while staying focused on it
- Animate a line from LA to NY with camera following the route
- Add additional stops (e.g. Paris) with 3D landmark animations (Eiffel Tower)

**Key techniques:** Map rendering, camera zoom/pan, animated path/line drawing, 3D object rendering (Three.js/R3F), multi-stop route sequencing.

## When to use

Use this skills whenever you are dealing with Remotion code to obtain the domain-specific knowledge.

## How to use

Read individual rule files for detailed explanations and code examples:

- [rules/3d.md](rules/3d.md) - 3D content in Remotion using Three.js and React Three Fiber
- [rules/animations.md](rules/animations.md) - Fundamental animation skills for Remotion
- [rules/assets.md](rules/assets.md) - Importing images, videos, audio, and fonts into Remotion
- [rules/audio.md](rules/audio.md) - Using audio and sound in Remotion - importing, trimming, volume, speed, pitch
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - Dynamically set composition duration, dimensions, and props
- [rules/can-decode.md](rules/can-decode.md) - Check if a video can be decoded by the browser using Mediabunny
- [rules/charts.md](rules/charts.md) - Chart and data visualization patterns for Remotion
- [rules/compositions.md](rules/compositions.md) - Defining compositions, stills, folders, default props and dynamic metadata
- [rules/display-captions.md](rules/display-captions.md) - Displaying captions in Remotion with TikTok-style pages and word highlighting
- [rules/extract-frames.md](rules/extract-frames.md) - Extract frames from videos at specific timestamps using Mediabunny
- [rules/fonts.md](rules/fonts.md) - Loading Google Fonts and local fonts in Remotion
- [rules/get-audio-duration.md](rules/get-audio-duration.md) - Getting the duration of an audio file in seconds with Mediabunny
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) - Getting the width and height of a video file with Mediabunny
- [rules/get-video-duration.md](rules/get-video-duration.md) - Getting the duration of a video file in seconds with Mediabunny
- [rules/gifs.md](rules/gifs.md) - Displaying GIFs synchronized with Remotion's timeline
- [rules/images.md](rules/images.md) - Embedding images in Remotion using the Img component
- [rules/import-srt-captions.md](rules/import-srt-captions.md) - Importing .srt subtitle files into Remotion using @remotion/captions
- [rules/launchpad-animations.md](rules/launchpad-animations.md) - Pro animations (FadeIn, SlideUp, TextReveal) from trycua/launchpad
- [rules/lottie.md](rules/lottie.md) - Embedding Lottie animations in Remotion
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) - Measuring DOM element dimensions in Remotion
- [rules/measuring-text.md](rules/measuring-text.md) - Measuring text dimensions, fitting text to containers, and checking overflow
- [rules/sequencing.md](rules/sequencing.md) - Sequencing patterns for Remotion - delay, trim, limit duration of items
- [rules/tailwind.md](rules/tailwind.md) - Using TailwindCSS in Remotion
- [rules/text-animations.md](rules/text-animations.md) - Typography and text animation patterns for Remotion
- [rules/timing.md](rules/timing.md) - Interpolation curves in Remotion - linear, easing, spring animations
- [rules/transcribe-captions.md](rules/transcribe-captions.md) - Transcribing audio to generate captions in Remotion
- [rules/transitions.md](rules/transitions.md) - Scene transition patterns for Remotion
- [rules/trimming.md](rules/trimming.md) - Trimming patterns for Remotion - cut the beginning or end of animations
- [rules/videos.md](rules/videos.md) - Embedding videos in Remotion - trimming, volume, speed, looping, pitch
