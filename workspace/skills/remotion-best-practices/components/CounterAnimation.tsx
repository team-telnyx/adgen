import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";

export interface CounterAnimationProps {
  /** Target number to count up to */
  targetValue: number;
  /** Duration of the count animation in frames */
  duration?: number;
  /** Animation delay in frames */
  delay?: number;
  /** Prefix string (e.g., "$" or "↑") */
  prefix?: string;
  /** Suffix string (e.g., "%" or "ms") */
  suffix?: string;
  /** Font size in pixels */
  fontSize?: number;
  /** Text color */
  color?: string;
  /** Number of decimal places */
  decimals?: number;
  /** Show glow effect */
  glow?: boolean;
}

export const CounterAnimation: React.FC<CounterAnimationProps> = ({
  targetValue,
  duration = 60,
  delay = 0,
  prefix = "",
  suffix = "",
  fontSize = 64,
  color = COLORS.telnyxGreen,
  decimals = 0,
  glow = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const localFrame = frame - delay;
  
  // Ease out progress for smooth deceleration
  const rawProgress = interpolate(localFrame, [0, duration], [0, 1], {
    extrapolateRight: "clamp",
  });
  
  // Apply ease-out curve
  const easedProgress = 1 - Math.pow(1 - rawProgress, 3);
  
  const currentValue = easedProgress * targetValue;
  
  const popScale = spring({
    frame: localFrame,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  const formattedValue = currentValue.toFixed(decimals);

  return (
    <div
      style={{
        fontFamily: FONTS.sans,
        fontSize,
        fontWeight: 700,
        color,
        transform: `scale(${interpolate(popScale, [0, 1], [0.5, 1])})`,
        textShadow: glow
          ? `0 0 20px ${color}66, 0 0 40px ${color}33`
          : "none",
      }}
    >
      {prefix}
      {formattedValue}
      {suffix}
    </div>
  );
};
