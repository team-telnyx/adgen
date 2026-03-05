import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { ReactNode } from "react";

export interface ClipRevealProps {
  children: ReactNode;
  delay?: number;
  durationInFrames?: number;
  direction?: "left" | "right";
}

export const ClipReveal: React.FC<ClipRevealProps> = ({
  children,
  delay = 0,
  durationInFrames = 25,
  direction = "left",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  const clipInset =
    direction === "left"
      ? `inset(0 ${100 - progress * 100}% 0 0)`
      : `inset(0 0 0 ${100 - progress * 100}%)`;

  return (
    <span style={{ clipPath: clipInset, display: "inline-block" }}>
      {children}
    </span>
  );
};
