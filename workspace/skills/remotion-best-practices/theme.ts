// Telnyx brand theme constants for Remotion templates
// Colors, fonts, spacing, and common animation durations

// Brand colors
export const COLORS = {
  background: "#000000",
  backgroundLight: "#1a1a1a",
  text: "#FFFFFF",
  textMuted: "#888888",
  telnyxGreen: "#00E3AA",
  telnyxGreenDim: "rgba(0, 227, 170, 0.15)",
  error: "#E53E3E",
} as const;

// Typography
// PP Formula: Telnyx branded heading font (load via @font-face in compositions)
// Inter: Body text (available via @remotion/google-fonts or local file)
export const FONTS = {
  heading: '"PP Formula", "Inter", system-ui, sans-serif',
  sans: '"Inter", system-ui, -apple-system, sans-serif',
  mono: '"JetBrains Mono", "Courier New", monospace',
} as const;

// Font sizes
export const FONT_SIZES = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 24,
  "2xl": 32,
  "3xl": 48,
  "4xl": 64,
  "5xl": 80,
} as const;

// Spacing scale (in pixels)
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  "2xl": 48,
  "3xl": 64,
} as const;

// Border radius
export const RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  "2xl": 24,
  full: 9999,
} as const;

// Common animation durations (in frames, assuming 30fps)
export const DURATIONS = {
  instant: 10,
  fast: 15,
  normal: 30,
  slow: 45,
  slower: 60,
} as const;

// Animation config defaults
export const SPRING_CONFIG = {
  bouncy: { damping: 12, stiffness: 100 },
  smooth: { damping: 15, stiffness: 80 },
  gentle: { damping: 20, stiffness: 60 },
} as const;
