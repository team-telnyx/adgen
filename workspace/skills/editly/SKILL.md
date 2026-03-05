---
name: editly
description: "Programmatic video editing with editly (Node.js + FFmpeg). Use when: user wants to cut, trim, splice, assemble, or edit existing video/image footage with code. Also for slideshows, trailers, social clips, audio mixing, subtitle overlays, and batch video processing. Don't use when: creating motion graphics from scratch (use remotion-best-practices), generating AI video (use veo), or extracting frames (use video-frames)."
homepage: https://github.com/mifi/editly
metadata:
  tags: editly, video, editing, ffmpeg, declarative, slideshow
---

# editly - Declarative Video Editing

Editly is a Node.js CLI and library for declarative NLE (non-linear video editing). Define edits as JSON5 specs or JS objects. No GUI needed. Streaming-based (no intermediate files, fast, low disk usage).

## Platform Compatibility Note

Editly uses `headless-gl` for GPU-accelerated transitions. This can be tricky to compile on some platforms (notably macOS ARM). If you encounter GL-related errors:

1. **Disable transitions**: Use `transition: null` in your specs
2. **Use built-in transitions only**: `directional-left`, `directional-right`, `directional-up`, `directional-down`, `dummy`
3. **Install with build-from-source**: `npm install -g --build-from-source editly`

Most other features (video, audio, images, text layers) work without GL.

---

## CLI Usage

```bash
# Quick assembly from clips/images/titles with music
editly title:'Intro' clip1.mp4 clip2.mp4 img1.jpg title:'END' \
  --audio-file-path music.mp3 --keep-source-audio --fast --out output.mp4

# From JSON5 spec (full control)
editly spec.json5 --out output.mp4

# GIF output
editly spec.json5 --out output.gif
```

### CLI Options
```
--out, -o PATH              Output path (.mp4, .mkv, .gif)
--fast, -f                  Low-res/FPS preview mode (use for testing!)
--width WIDTH               Output width (default: 640, or first video's width without --fast)
--height HEIGHT             Output height (auto from aspect ratio)
--fps FPS                   Output framerate (default: first video's FPS or 25)
--audio-file-path PATH      Background music
--loop-audio                Loop audio to match video length
--keep-source-audio         Preserve audio from input video clips
--transition-duration SEC   Default transition duration (default: 0.5)
--transition-name NAME      Default transition type (default: random)
--clip-duration SEC         Default clip duration (default: 4)
--font-path PATH            Default .ttf font
--output-volume VOL         Output volume (0.5 or '10dB')
--allow-remote-requests     Allow http/https URLs as input paths
```

---

## Full Edit Spec Structure

```json5
{
  outPath: "./output.mp4",        // .mp4, .mkv, or .gif
  width: 1920,                    // Default: 640 (or first video width)
  height: 1080,                   // Default: auto from first video aspect ratio
  fps: 30,                        // Default: first video FPS or 25
  fast: false,                    // Preview mode (low res + low FPS)
  allowRemoteRequests: false,     // Allow URLs as layer paths

  // Custom ffmpeg output args (overrides default h264)
  customOutputArgs: ["-c:v", "libx264", "-crf", "18", "-preset", "slow"],

  // Defaults inherited by all clips/layers
  defaults: {
    duration: 4,                  // Seconds per clip (if not specified per-clip)
    transition: null,             // Transition config or null for hard cuts
    layer: {
      fontPath: "./font.ttf",    // Default font for all text layers
    },
    layerType: {                  // Per-type defaults
      "fill-color": { color: "#ff6666" },
      "image-overlay": { width: 0.1 },
    },
  },

  // THE MAIN CONTENT: array of clips
  clips: [
    {
      duration: 5,                // Override default duration for this clip
      transition: null,           // Override transition for this clip
      layers: [ /* layer objects */ ],
    }
  ],

  // === AUDIO CONFIG ===
  audioFilePath: "./music.mp3",   // Background music track
  loopAudio: false,               // Loop if shorter than video
  keepSourceAudio: false,         // Keep audio from source video clips
  clipsAudioVolume: 1,            // Volume of clip audio relative to audioTracks
  outputVolume: 1,                // Final master volume (number or "10dB")

  // Arbitrary additional audio tracks with precise timing
  audioTracks: [
    {
      path: "./voiceover.mp3",
      mixVolume: 1,               // Relative volume
      cutFrom: 0,                 // Start point in source file (seconds)
      cutTo: 30,                  // End point in source file
      start: 5,                   // When to begin playing in final video (seconds)
    }
  ],

  // Audio normalization / auto-ducking
  audioNorm: {
    enable: false,                // Enable to auto-lower music when voice is present
    gaussSize: 5,                 // Smoothing (lower = more responsive)
    maxGain: 30,                  // Max volume boost
  },

  // Debug
  enableFfmpegLog: false,
  verbose: false,
}
```

---

## Layer Types (Complete Reference)

### video
Video clip. The workhorse layer.
```json5
{
  type: "video",
  path: "./video.mp4",
  cutFrom: 0,                    // Start time in source (seconds)
  cutTo: 10,                     // End time in source (seconds)
  // If clip.duration is set and differs from cutTo-cutFrom, video auto-speeds to fit
  // Audio speed limited to 0.5x - 100x

  // Positioning (all values 0-1, relative to output dimensions)
  width: 1,                      // 1 = full width
  height: 1,                     // 1 = full height
  left: 0,                       // X position (0 = left edge)
  top: 0,                        // Y position (0 = top edge)
  originX: "left",               // "left" or "right" (anchor point)
  originY: "top",                // "top" or "bottom" (anchor point)

  resizeMode: "contain-blur",    // How to handle aspect ratio mismatch (see Resize Modes)
  mixVolume: 1,                  // Audio volume when mixing
}
```

**Auto-speed:** If `duration: 3` but cutTo-cutFrom = 6, video plays at 2x speed. If cutTo-cutFrom = 1.5, video plays at 0.5x speed.

### image
Static image with optional Ken Burns effect.
```json5
{
  type: "image",
  path: "./photo.jpg",
  resizeMode: "contain-blur",
  zoomDirection: "in",           // "in", "out", "left", "right", or null (no animation)
  zoomAmount: 0.1,               // Intensity of zoom (default: 0.1)
}
```

### image-overlay
Positioned overlay. Supports PNG/SVG transparency. Great for logos, watermarks, stickers.
```json5
{
  type: "image-overlay",
  path: "./logo.png",
  width: 0.2,                    // Relative to output (0-1)
  height: 0.1,                   // Optional (maintains aspect if omitted)

  // Position: shortcut string OR object
  position: "top-right",
  // Shortcuts: "top", "bottom", "center", "top-left", "top-right",
  //   "center-left", "center-right", "bottom-left", "bottom-right"
  // OR object: { x: 0.95, y: 0.05, originX: "right", originY: "top" }

  // Timing within clip
  start: 0,                      // When overlay appears (seconds into clip)
  stop: 2,                       // When overlay disappears

  zoomDirection: null,           // Optional Ken Burns
}
```

### title
Text overlay, positioned anywhere.
```json5
{
  type: "title",
  text: "My Title",
  textColor: "#ffffff",
  fontPath: "./font.ttf",        // Optional, overrides default
  position: "center",            // Same position options as image-overlay
  zoomDirection: null,
}
```

### title-background
Full-screen title card with background. Use for intros, outros, section dividers.
```json5
{
  type: "title-background",
  text: "Welcome\nMultiline works",    // \n for line breaks
  textColor: "#ffffff",
  fontPath: "./font.ttf",
  background: {
    type: "fill-color",                // or "linear-gradient" or "radial-gradient"
    color: "#000000",                  // for fill-color
    // colors: ["#02aab0", "#00cdac"], // for gradients (array of 2+ colors)
  }
}
```

### subtitle
Caption text at bottom. Auto-wraps long text.
```json5
{
  type: "subtitle",
  text: "Long caption text that wraps automatically...",
  textColor: "#ffffff",
  backgroundColor: "rgba(0,0,0,0.5)", // Optional semi-transparent background
  fontPath: "./font.ttf",
}
```

### news-title
Breaking news style banner.
```json5
{
  type: "news-title",
  text: "BREAKING NEWS",
  textColor: "#ffffff",
  backgroundColor: "#d02a42",
  position: "top-left",
}
```

### slide-in-text
Text that animates in by sliding.
```json5
{
  type: "slide-in-text",
  text: "Sliding text",
  textColor: "#fff",
  fontSize: 0.05,                // Relative to height
  charSpacing: 1,
  position: { x: 0.04, y: 0.93, originY: "bottom" },
}
```

### fill-color
Solid color background.
```json5
{ type: "fill-color", color: "#ff6666" }  // Omit color for random
```

### linear-gradient / radial-gradient
```json5
{ type: "linear-gradient", colors: ["#ff0000", "#0000ff"] }
{ type: "radial-gradient", colors: ["#ff0000", "#0000ff"] }
```

### rainbow-colors
Animated cycling rainbow background.
```json5
{ type: "rainbow-colors" }
```

### audio
Audio track tied to a clip's timeline.
```json5
{
  type: "audio",
  path: "./sound.mp3",
  cutFrom: 0,
  cutTo: 10,
  mixVolume: 1,
}
```

### detached-audio
Audio with timing relative to clip start (independent of video speed changes). Good for voiceovers.
```json5
{
  type: "detached-audio",
  path: "./voiceover.mp3",
  mixVolume: 50,
  cutFrom: 2,                   // Start from 2s into the audio file
  start: 1,                     // Begin 1s after clip starts
}
```

### canvas
Custom HTML5 Canvas rendering via JS function.
```javascript
function myCanvas({ canvas }) {
  return {
    async onRender(progress) {   // progress: 0 to 1 over clip duration
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = `hsl(${progress * 360}, 70%, 50%)`;
      ctx.fillRect(0, 0, canvas.width * progress, canvas.height);
    },
    onClose() {}
  };
}
// Usage: { type: "canvas", func: myCanvas }
```

### fabric
Custom Fabric.js rendering (richer than canvas: text, shapes, images, filters).
```javascript
import { registerFont } from "canvas";
registerFont("./font.ttf", { family: "MyFont" });

function myFabric({ width, height, fabric }) {
  return {
    async onRender(progress, canvas) {
      canvas.backgroundColor = "hsl(33, 100%, 50%)";
      const text = new fabric.FabricText(`${Math.floor(progress * 100)}%`, {
        left: width / 2, top: height / 2,
        originX: "center", originY: "center",
        fontSize: 60, fontFamily: "MyFont", fill: "white",
      });
      canvas.add(text);
    },
    onClose() {}
  };
}
// Usage: { type: "fabric", func: myFabric }
```

### fabricImagePostProcessing
Not a layer type, but a property on video/image layers. Applies Fabric.js effects.
```json5
{
  type: "video",
  path: "./video.mp4",
  fabricImagePostProcessing: async ({ image, fabric, canvas }) => {
    // Example: circular mask
    const circle = new fabric.Circle({
      radius: Math.min(image.width, image.height) * 0.4,
      originX: "center", originY: "center",
    });
    image.set({ clipPath: circle });
  }
}
```

### gl
Custom GLSL fragment shaders. Requires working headless-gl installation.
```json5
{
  type: "gl",
  fragmentPath: "./shader.frag",
  vertexPath: "./vertex.vert",   // Optional
  speed: 1,
}
// Uniforms provided: uniform float time; uniform vec2 resolution;
```

---

## Resize Modes

| Mode | Behavior | Best For |
|------|----------|----------|
| `contain` | Fit entirely, black letterbox bars | Preserving full content |
| `contain-blur` | Fit entirely, blurred copy fills bars | Best default, avoids ugly black bars |
| `cover` | Fill screen, crop edges as needed | Full-bleed, when cropping is OK |
| `stretch` | Distort to fit dimensions | Almost never use this |

---

## Transitions

Editly supports [gl-transitions](https://gl-transitions.com/gallery) (~90 types). Note: GL transitions require headless-gl to compile correctly on your platform.

**Popular GL transitions:** fade, fadecolor, fadegrayscale, crosszoom, simplezoom, dreamyzoom, directionalwipe, directionalwarp, circle, circleopen, circlecrop, radial, swap, doorway, cube, wind, ripple, perlin, morph, glitchdisplace

**Built-in (no GL needed):** directional-left, directional-right, directional-up, directional-down, random, dummy

```json5
// Per-clip transition
{ transition: { name: "fade", duration: 0.8 } }

// Disable transition for one clip
{ transition: null }

// Audio-only crossfade (video cuts instantly, audio fades)
{ transition: { name: "dummy", duration: 0.5, audioOutCurve: "tri", audioInCurve: "tri" } }
```

**Audio crossfade curves:** tri, exp, log, ipar, hann (see FFmpeg afade docs)

---

## Audio Best Practices

### Auto-ducking (lower music when voice plays)
```json5
{
  keepSourceAudio: true,
  clipsAudioVolume: 50,          // High value = voice "wins"
  audioTracks: [
    { path: "./music.mp3", mixVolume: 1 },
    { path: "./voiceover.mp3", mixVolume: 50 },
  ],
  audioNorm: { enable: true, gaussSize: 3, maxGain: 100 },
}
```

### Multi-track with precise timing
```json5
{
  audioTracks: [
    { path: "./bg-music.mp3", mixVolume: 0.3, cutFrom: 30 },
    { path: "./voiceover.mp3", mixVolume: 1.0, start: 5 },
    { path: "./sfx-ding.mp3", mixVolume: 0.8, start: 10, cutFrom: 0, cutTo: 2 },
  ]
}
```

### Looping short music
```json5
{ audioFilePath: "./short-loop.mp3", loopAudio: true }
```

---

## Platform Presets

| Platform | Width | Height | Aspect | FPS |
|----------|-------|--------|--------|-----|
| YouTube | 1920 | 1080 | 16:9 | 30 |
| YouTube 4K | 3840 | 2160 | 16:9 | 60 |
| Instagram Feed | 1080 | 1080 | 1:1 | 30 |
| Instagram Story/Reels/TikTok | 1080 | 1920 | 9:16 | 30 |
| Instagram Portrait | 1080 | 1350 | 4:5 | 30 |
| Twitter/X | 1280 | 720 | 16:9 | 30 |
| LinkedIn | 1080 | 1080 | 1:1 | 30 |

---

## Complete Templates

### Slideshow with Ken Burns + Music
```json5
{
  outPath: "./slideshow.mp4",
  width: 1920, height: 1080, fps: 30,
  audioFilePath: "./music.mp3",
  loopAudio: true,
  defaults: { duration: 4, transition: null },
  clips: [
    { layers: [{ type: "image", path: "./img1.jpg", zoomDirection: "in" }] },
    { layers: [{ type: "image", path: "./img2.jpg", zoomDirection: "out" }] },
    { layers: [{ type: "image", path: "./img3.jpg", zoomDirection: "left" }] },
  ]
}
```

### Video Trailer (fast cuts + titles)
```json5
{
  outPath: "./trailer.mp4",
  width: 1920, height: 1080, fps: 30,
  defaults: { transition: null },
  clips: [
    {
      duration: 2,
      layers: [{ type: "title-background", text: "COMING SOON", background: { type: "radial-gradient", colors: ["#1a1a2e", "#16213e"] } }]
    },
    {
      duration: 1.5,
      layers: [
        { type: "video", path: "./clip1.mp4", cutFrom: 5, cutTo: 6.5 },
        { type: "title", text: "FEATURE 1", position: "bottom" }
      ]
    },
    {
      duration: 1.5,
      layers: [
        { type: "video", path: "./clip2.mp4", cutFrom: 12, cutTo: 13.5 },
        { type: "title", text: "FEATURE 2", position: "bottom" }
      ]
    },
    {
      duration: 3,
      layers: [{ type: "title-background", text: "AVAILABLE NOW", background: { type: "fill-color", color: "#000" } }]
    }
  ],
  audioFilePath: "./trailer-music.mp3"
}
```

### Tutorial (screen recording + subtitles + sections)
```json5
{
  outPath: "./tutorial.mp4",
  width: 1920, height: 1080,
  keepSourceAudio: true,
  defaults: { transition: null, layer: { fontPath: "./mono-font.ttf" } },
  clips: [
    {
      duration: 5,
      layers: [{ type: "title-background", text: "How to Use X\nStep-by-step", background: { type: "fill-color", color: "#1a1a2e" } }]
    },
    {
      layers: [
        { type: "video", path: "./screen-recording.mp4", cutFrom: 0, cutTo: 30 },
        { type: "subtitle", text: "First, open the app and go to settings.", backgroundColor: "rgba(0,0,0,0.6)" }
      ]
    },
    {
      duration: 3,
      layers: [
        { type: "fill-color", color: "#333" },
        { type: "title", text: "Key Takeaway", position: "center" },
        { type: "slide-in-text", text: "Always save your work!", position: { x: 0.5, y: 0.7, originX: "center" } }
      ]
    }
  ]
}
```

### Social Clip (vertical, Instagram/TikTok)
```json5
{
  outPath: "./reel.mp4",
  width: 1080, height: 1920, fps: 30,
  audioFilePath: "./trending-audio.mp3",
  defaults: { transition: null },
  clips: [
    {
      duration: 2,
      layers: [
        { type: "video", path: "./clip1.mp4", resizeMode: "cover" },
        { type: "title", text: "PART 1", position: "top" }
      ]
    },
    {
      duration: 2,
      layers: [
        { type: "video", path: "./clip2.mp4", resizeMode: "cover" },
        { type: "title", text: "PART 2", position: "top" }
      ]
    },
    {
      duration: 3,
      layers: [
        { type: "title-background", text: "Follow for more!", background: { type: "linear-gradient", colors: ["#667eea", "#764ba2"] } }
      ]
    }
  ]
}
```

### Picture-in-Picture (webcam over screen recording)
```json5
{
  outPath: "./pip.mp4",
  width: 1920, height: 1080,
  keepSourceAudio: true,
  defaults: { transition: null },
  clips: [
    {
      layers: [
        { type: "video", path: "./screen-recording.mp4" },
        {
          type: "video", path: "./webcam.mp4",
          resizeMode: "cover",
          width: 0.25, height: 0.25,
          left: 0.97, top: 0.03,
          originX: "right", originY: "top"
        }
      ]
    }
  ]
}
```

### Podcast (square, with cover art + audio)
```json5
{
  outPath: "./podcast-clip.mp4",
  width: 1080, height: 1080, fps: 30,
  defaults: { transition: null },
  clips: [
    {
      duration: 300,
      layers: [
        { type: "image", path: "./podcast-cover.jpg" },
        { type: "subtitle", text: "Episode 42: The Big Topic", backgroundColor: "rgba(0,0,0,0.7)" }
      ]
    }
  ],
  audioTracks: [{ path: "./podcast-audio.mp3", mixVolume: 1, cutFrom: 120, cutTo: 420 }]
}
```

### B-Roll Insert (main video with cutaway)
```json5
{
  clips: [
    {
      duration: 10,
      layers: [
        { type: "video", path: "./interview.mp4", cutFrom: 0, cutTo: 10 },
        // B-roll appears from 3-6 seconds into this clip
        {
          type: "video", path: "./broll.mp4",
          cutFrom: 0, cutTo: 3,
          width: 1, height: 1,
          // Use start/stop to control when the overlay appears
        }
      ]
    }
  ]
}
```

### Remotion + Editly Pipeline
```json5
// 1. Render Remotion compositions to MP4 first:
//    npx remotion render src/index.ts Intro out/intro.mp4
//    npx remotion render src/index.ts LowerThird out/lower-third.mp4
//    npx remotion render src/index.ts Outro out/outro.mp4
// 2. Assemble with editly:
{
  outPath: "./final.mp4",
  width: 1920, height: 1080,
  keepSourceAudio: true,
  defaults: { transition: null },
  clips: [
    { layers: [{ type: "video", path: "./out/intro.mp4" }] },
    {
      layers: [
        { type: "video", path: "./main-content.mp4" },
        { type: "image-overlay", path: "./logo.png", width: 0.1, position: "top-right" }
      ]
    },
    { layers: [{ type: "video", path: "./out/outro.mp4" }] }
  ],
  audioFilePath: "./bg-music.mp3",
  loopAudio: true,
  clipsAudioVolume: 0.8
}
```

---

## Key Behaviors to Remember

1. **Without --fast:** Uses first video's actual width/height/fps. With --fast: uses reduced resolution.
2. **Duration vs cutFrom/cutTo:** `duration` = how long the clip appears in output. `cutFrom/cutTo` = which segment of source to use. If they differ, video speed adjusts automatically.
3. **Layer order matters:** First layer is the background. Later layers render on top.
4. **Clips with no duration:** If a clip has a video layer and no explicit duration, it uses the video's natural length (or cutTo-cutFrom).
5. **Transition overlap:** A transition eats time from both clips. Transition duration can't exceed half of either clip's duration.
6. **Font handling:** Set `defaults.layer.fontPath` for project-wide font, or per-layer with `fontPath`.
7. **Remote URLs:** Set `allowRemoteRequests: true` to use http/https URLs as layer paths.
8. **GIF output:** Just set `outPath: "./output.gif"`. Editly handles conversion.
9. **WebP output:** `outPath: "./output.webp"` with `customOutputArgs: ["-compression_level", "5", "-qscale", "60", "-vcodec", "libwebp"]`

## Troubleshooting

- **No audio:** Set `keepSourceAudio: true` for video audio, or `audioFilePath` for music
- **Audio out of sync:** Some source videos have mismatched audio/video track lengths. Check with `mediainfo`
- **Aspect ratio wrong:** Set explicit `width`/`height` and use `resizeMode: "contain-blur"`
- **Slow render:** Use `--fast` for testing, remove for final
- **GL/transition error:** headless-gl may not compile on your platform. Use `transition: null` or built-in transitions
- **Video too fast/slow:** Check if `duration` conflicts with `cutFrom`/`cutTo` range
- **No module found:** Try `npm uninstall -g editly && npm install -g --build-from-source editly`
