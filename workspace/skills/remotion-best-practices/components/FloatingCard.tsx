import { interpolate, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { ReactNode } from "react";

export interface FloatingCardProps {
  children: ReactNode;
  delay?: number;
  direction?: "left" | "right" | "bottom";
  width?: number;
  padding?: number;
  borderRadius?: number;
  shadowIntensity?: "light" | "medium" | "heavy";
}

export const FloatingCard: React.FC<FloatingCardProps> = ({
  children,
  delay = 0,
  direction = "right",
  width = 400,
  padding = 32,
  borderRadius = 16,
  shadowIntensity = "medium",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const shadowMap = {
    light: "0 8px 24px rgba(0,0,0,0.08)",
    medium: "0 20px 60px rgba(0,0,0,0.3)",
    heavy: "0 30px 80px rgba(0,0,0,0.4)",
  };

  const slideProgress = interpolate(
    frame - delay,
    [0, 30],
    [1, 0],
    { easing: Easing.out(Easing.cubic), extrapolateRight: "clamp" }
  );

  const opacity = interpolate(frame - delay, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const getTransform = () => {
    const dist = direction === "bottom" ? 0 : 300;
    const x = direction === "right" ? slideProgress * dist : direction === "left" ? -slideProgress * dist : 0;
    const y = direction === "bottom" ? slideProgress * 300 : 0;
    const rotate = slideProgress * 5;
    return `translate(${x}px, ${y}px) rotate(${rotate}deg)`;
  };

  return (
    <div
      style={{
        width,
        padding,
        backgroundColor: "#FFFFFF",
        borderRadius,
        boxShadow: shadowMap[shadowIntensity],
        transform: getTransform(),
        opacity,
      }}
    >
      {children}
    </div>
  );
};
