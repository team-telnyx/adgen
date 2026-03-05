import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { COLORS, FONTS, SPRING_CONFIG, DURATIONS } from "../theme";

export type TextVariant = "fadeIn" | "slideUp" | "typewriter";

export interface AnimatedTextProps {
  text: string;
  variant?: TextVariant;
  delay?: number;
  style?: React.CSSProperties;
  fontSize?: number;
  fontWeight?: number | string;
  color?: string;
}

export const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  variant = "fadeIn",
  delay = 0,
  style,
  fontSize = 24,
  fontWeight = 400,
  color = COLORS.text,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);

  // Fade in animation
  const opacity = interpolate(
    adjustedFrame,
    [0, DURATIONS.normal],
    [0, 1],
    { extrapolateRight: "clamp" }
  );

  // Slide up animation using spring
  const slideProgress = spring({
    frame: adjustedFrame,
    fps,
    config: SPRING_CONFIG.smooth,
  });

  const translateY = interpolate(slideProgress, [0, 1], [30, 0]);

  // Typewriter animation - reveal characters over time
  const charReveal = interpolate(
    adjustedFrame,
    [0, text.length * 3],
    [0, text.length],
    { extrapolateRight: "clamp" }
  );

  // Build transform based on variant
  const transform =
    variant === "slideUp"
      ? `translateY(${translateY}px)`
      : variant === "fadeIn"
      ? "translateY(0)"
      : "translateY(0)";

  // For typewriter, we slice the text
  const displayText = variant === "typewriter" ? text.slice(0, charReveal) : text;

  return (
    <span
      style={{
        fontFamily: FONTS.sans,
        fontSize,
        fontWeight,
        color,
        display: "inline-block",
        opacity: variant === "typewriter" ? 1 : opacity,
        transform,
        ...style,
      }}
    >
      {displayText}
      {variant === "typewriter" && charReveal < text.length && (
        <span
          style={{
            borderRight: `2px solid ${color}`,
            animation: "none",
            marginLeft: 2,
          }}
        />
      )}
    </span>
  );
};
