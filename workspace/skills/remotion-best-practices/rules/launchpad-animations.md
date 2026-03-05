# Launchpad Animations (FadeIn, SlideUp, TextReveal)

High-quality, configurable animation components from `trycua/launchpad`. Use these for professional-grade motion.

## FadeIn

Smooth opacity fade with optional directional movement.

```tsx
import { AbsoluteFill, useCurrentFrame, interpolate, Easing } from "remotion";
import { ReactNode } from "react";

interface FadeInProps {
  children: ReactNode;
  durationInFrames?: number;
  delay?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  distance?: number;
  easing?: (t: number) => number;
  style?: React.CSSProperties;
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  durationInFrames = 20,
  delay = 0,
  direction = "up",
  distance = 30,
  easing = Easing.out(Easing.cubic),
  style,
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = Math.max(0, frame - delay);

  const opacity = interpolate(adjustedFrame, [0, durationInFrames], [0, 1], {
    extrapolateRight: "clamp",
    easing,
  });

  const getTransform = () => {
    if (direction === "none") return "none";

    const progress = interpolate(adjustedFrame, [0, durationInFrames], [distance, 0], {
      extrapolateRight: "clamp",
      easing,
    });

    switch (direction) {
      case "up":
        return `translateY(${progress}px)`;
      case "down":
        return `translateY(-${progress}px)`;
      case "left":
        return `translateX(${progress}px)`;
      case "right":
        return `translateX(-${progress}px)`;
      default:
        return "none";
    }
  };

  return (
    <div style={{ opacity, transform: getTransform(), ...style }}>
      {children}
    </div>
  );
};
```

## SlideUp

Classic slide-up reveal.

```tsx
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { ReactNode } from "react";

interface SlideUpProps {
  children: ReactNode;
  durationInFrames?: number;
  delay?: number;
  distance?: number;
  easing?: (t: number) => number;
  style?: React.CSSProperties;
}

export const SlideUp: React.FC<SlideUpProps> = ({
  children,
  durationInFrames = 20,
  delay = 0,
  distance = 50,
  easing = Easing.out(Easing.cubic),
  style,
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = Math.max(0, frame - delay);

  const translateY = interpolate(adjustedFrame, [0, durationInFrames], [distance, 0], {
    extrapolateRight: "clamp",
    easing,
  });

  const opacity = interpolate(adjustedFrame, [0, durationInFrames * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        transform: `translateY(${translateY}px)`,
        opacity,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
```

## TextReveal

Clip-path text reveal animation (masking effect).

```tsx
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { ReactNode } from "react";

interface TextRevealProps {
  children: ReactNode;
  durationInFrames?: number;
  delay?: number;
  direction?: "left" | "right";
  easing?: (t: number) => number;
  style?: React.CSSProperties;
  maskColor?: string;
}

export const TextReveal: React.FC<TextRevealProps> = ({
  children,
  durationInFrames = 30,
  delay = 0,
  direction = "left",
  easing = Easing.inOut(Easing.cubic),
  style,
  maskColor = "#000",
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = Math.max(0, frame - delay);

  const clipProgress = interpolate(adjustedFrame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
    easing,
  });

  const clipPath =
    direction === "left"
      ? `inset(0 ${100 - clipProgress}% 0 0)`
      : `inset(0 0 0 ${100 - clipProgress}%)`;

  return (
    <div style={{ position: "relative", ...style }}>
      <div style={{ clipPath }}>{children}</div>
    </div>
  );
};
```
