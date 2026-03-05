// Telnyx brand theme for AdGen video compositions

export const COLORS = {
  black: '#000000',
  cream: '#F5F0E8',
  green: '#00C26E',
  citron: '#D4E510',
  voiceAiPink: '#FF6B9D',
  white: '#FFFFFF',
  textMuted: '#888888',
  backgroundLight: '#1a1a1a',
} as const;

export const FONTS = {
  heading: '"PP Formula", "Inter", system-ui, sans-serif',
  sans: '"Inter", system-ui, -apple-system, sans-serif',
} as const;

export const FONT_SIZES = {
  sm: 14,
  md: 18,
  lg: 24,
  xl: 36,
  '2xl': 48,
  '3xl': 64,
  '4xl': 80,
  '5xl': 100,
} as const;

export const DURATIONS = {
  fast: 15,
  normal: 30,
  slow: 45,
} as const;

export const SPRING_CONFIG = {
  bouncy: { damping: 12, stiffness: 100 },
  smooth: { damping: 15, stiffness: 80 },
  gentle: { damping: 20, stiffness: 60 },
} as const;

// Format dimensions
export const FORMAT_DIMENSIONS: Record<string, { width: number; height: number }> = {
  landscape: { width: 1920, height: 1080 },
  square: { width: 1080, height: 1080 },
  vertical: { width: 1080, height: 1920 },
};
