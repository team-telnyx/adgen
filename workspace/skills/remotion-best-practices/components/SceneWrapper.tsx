import React from "react";
import { useCurrentFrame, interpolate, AbsoluteFill } from "remotion";
import { COLORS } from "../theme";

export interface SceneWrapperProps {
  children: React.ReactNode;
  from: number;
  durationInFrames: number;
  backgroundColor?: string;
}

export const SceneWrapper: React.FC<SceneWrapperProps> = ({
  children,
  from,
  durationInFrames,
  backgroundColor = COLORS.background,
}) => {
  const frame = useCurrentFrame();

  // Calculate where we are relative to this scene
  const sceneFrame = frame - from;

  // Fade in at start (first 15% of scene)
  const fadeInOpacity = interpolate(
    sceneFrame,
    [0, durationInFrames * 0.15],
    [0, 1],
    { extrapolateRight: "clamp" }
  );

  // Fade out at end (last 15% of scene)
  const fadeOutOpacity = interpolate(
    sceneFrame,
    [durationInFrames * 0.85, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Combined opacity
  const opacity = Math.min(fadeInOpacity, fadeOutOpacity);

  // Skip rendering if outside scene bounds
  if (sceneFrame < 0 || sceneFrame >= durationInFrames) {
    return null;
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        opacity,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
