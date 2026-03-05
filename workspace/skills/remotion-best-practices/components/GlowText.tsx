import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";

export interface GlowTextProps {
  /** Text content to display */
  text: string;
  /** Font size in pixels */
  fontSize?: number;
  /** Text color (also determines glow color) */
  color?: string;
  /** Glow intensity (0-1) */
  glowIntensity?: number;
  /** Animation delay in frames */
  delay?: number;
  /** Animation variant */
  variant?: "fadeIn" | "slideUp" | "pulse";
  /** Additional styles */
  style?: React.CSSProperties;
}

export const GlowText: React.FC<GlowTextProps> = ({
  text,
  fontSize = 48,
  color = COLORS.telnyxGreen,
  glowIntensity = 0.6,
  delay = 0,
  variant = "fadeIn",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const localFrame = frame - delay;

  const progress = spring({
    frame: localFrame,
    fps,
    config: SPRING_CONFIG.smooth,
  });

  const opacity = interpolate(progress, [0, 1], [0, 1]);
  
  const translateY = variant === "slideUp" 
    ? interpolate(progress, [0, 1], [30, 0])
    : 0;

  // Pulse effect
  const pulseScale = variant === "pulse"
    ? 1 + Math.sin(frame * 0.1) * 0.02
    : 1;

  // Animated glow pulsing
  const glowPulse = 0.8 + Math.sin(frame * 0.08) * 0.2;

  return (
    <div
      style={{
        fontFamily: FONTS.sans,
        fontSize,
        fontWeight: 700,
        color,
        opacity,
        transform: `translateY(${translateY}px) scale(${pulseScale})`,
        textShadow: `
          0 0 10px ${color}${Math.round(glowIntensity * glowPulse * 100)
            .toString()
            .padStart(2, "0")},
          0 0 20px ${color}${Math.round(glowIntensity * glowPulse * 60)
            .toString()
            .padStart(2, "0")},
          0 0 40px ${color}${Math.round(glowIntensity * glowPulse * 40)
            .toString()
            .padStart(2, "0")}
        `,
        ...style,
      }}
    >
      {text}
    </div>
  );
};
