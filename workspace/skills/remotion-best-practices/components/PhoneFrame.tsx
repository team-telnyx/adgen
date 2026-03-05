import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { COLORS, SPRING_CONFIG } from "../theme";

export interface PhoneFrameProps {
  /** Content to render inside the phone screen */
  children?: React.ReactNode;
  /** Phone frame color (default: dark gray) */
  frameColor?: string;
  /** Screen background color */
  screenColor?: string;
  /** Width of the phone frame in pixels */
  width?: number;
  /** Show notch at top */
  showNotch?: boolean;
  /** Scale animation delay */
  delay?: number;
}

export const PhoneFrame: React.FC<PhoneFrameProps> = ({
  children,
  frameColor = "#1a1a1a",
  screenColor = "#000000",
  width = 320,
  showNotch = true,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const height = width * 2.1; // 9:19.5 aspect ratio

  const scaleProgress = spring({
    frame: frame - delay,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  const scale = interpolate(scaleProgress, [0, 1], [0.8, 1]);
  const opacity = interpolate(scaleProgress, [0, 1], [0, 1]);

  return (
    <div
      style={{
        width,
        height,
        backgroundColor: frameColor,
        borderRadius: width * 0.12,
        padding: width * 0.03,
        boxShadow: `
          0 0 0 ${width * 0.006}px #333,
          0 ${width * 0.05}px ${width * 0.15}px rgba(0, 0, 0, 0.5)
        `,
        transform: `scale(${scale})`,
        opacity,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Notch */}
      {showNotch && (
        <div
          style={{
            position: "absolute",
            top: width * 0.02,
            left: "50%",
            transform: "translateX(-50%)",
            width: width * 0.35,
            height: width * 0.04,
            backgroundColor: "#000",
            borderRadius: width * 0.02,
            zIndex: 10,
          }}
        />
      )}

      {/* Screen */}
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: screenColor,
          borderRadius: width * 0.1,
          overflow: "hidden",
          position: "relative",
        }}
      >
        {children}
      </div>

      {/* Home indicator */}
      <div
        style={{
          position: "absolute",
          bottom: width * 0.015,
          left: "50%",
          transform: "translateX(-50%)",
          width: width * 0.25,
          height: width * 0.012,
          backgroundColor: "#555",
          borderRadius: width * 0.006,
        }}
      />
    </div>
  );
};
