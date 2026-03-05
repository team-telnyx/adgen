# Remotion Best Practices Skill

Create high-quality promotional videos using Remotion (React-based video framework) and AI coding agents.

Built by Abhishek + Crabishek.

## Package Contents

| Component | Location | Description |
|-----------|----------|-------------|
| **Skill** | `SKILL.md` | Design standards, AI workflow, 29 rule files |
| **Components** | `components/` | 14 reusable motion components |
| **Templates** | `templates/` | 8 ready-to-use video compositions |
| **Theme** | `theme.ts` | Telnyx brand constants |
| **Spawn Template** | `spawn-template.md` | AI agent preamble for first-render quality |
| **Agent** | `agents/promo-video-creator/` | Sub-agent that uses this skill |

## Quick Start

1. **Use the agent:** `@promo-video-creator new "Product launch" --duration 30s`
2. **Or read the skill directly:** Point any coding agent to `SKILL.md`
3. **For AI spawns:** Paste `spawn-template.md` into every Remotion task prompt

## What's Included

### Design Standards
- Narrative arc for video structure (Why Now → What Changes → How It Works → Next Steps)
- One idea per scene principle
- Resolution standards (1080p minimum, never 720p)
- Template-first approach
- QA checklist for delivery

### AI Workflow (Critical)
- **One change at a time** - Single requests = better results
- **Section by section** - Build intro → content → CTA, not all at once
- **Feed Remotion docs** - Add `.md` to any remotion.dev URL for markdown
- **Use the spawn template** - Ensures first-render quality every time

### Components (14)
General-purpose: AnimatedText, SceneWrapper, CodeBlock, GlowText, CounterAnimation, StatReveal, FloatingCard, GradientMesh, RisingShapes, TextCut, ClipReveal, PhoneFrame, ChatBubble

Terminal/CLI-specific (legacy): MotionPatterns (TerminalZoom, TypewriterText, GlitchText, CLITableReveal, etc.)

### Templates (8)
- **ProductLaunch** - 6-scene product launch (hook → problem → intro → features → code → CTA)
- **ChatDemo** - Animated chat conversation (16:9 and 9:16)
- **PhoneScreenDemo** - Phone mockup with screen recording
- **DayInLifeAd** - Multi-scene storytelling ad
- **SocialAd** - Short-form vertical ad
- **CleanProductPromo** - Light-theme, minimal motion promo (Lemon/ElevenLabs style)
- **HowItWorks** - Step-by-step explainer
- **TTSLibraryPromo** - Example promo for ttslibrary.com

### Rules (29 files)
Detailed references for every Remotion feature: animations, audio, captions, 3D, charts, transitions, fonts, GIFs, images, Lottie, sequencing, Tailwind, timing, trimming, and more.

## Tips for Best Results

1. **Start with a template** - Don't build from scratch unless you need something truly custom
2. **One scene at a time** - Build and verify each scene before moving on
3. **Use spring() for organic motion** - Interpolate for linear, spring for natural
4. **Test early** - Render first 10 frames to catch errors before full render
5. **1080p minimum** - Always render at 1920x1080 for 16:9 or 1080x1920 for 9:16

## Migration Note

If you were using the old `MotionPatterns.tsx` (TerminalZoom, TypewriterText, GlitchText, CLITableReveal, etc.), it's still included in `components/MotionPatterns.tsx`. New components are additive and don't replace the terminal-specific patterns.
