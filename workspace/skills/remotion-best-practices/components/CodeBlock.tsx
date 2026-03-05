import React, { useMemo } from "react";
import { useCurrentFrame, interpolate, useVideoConfig } from "remotion";
import { COLORS, FONTS, RADIUS, DURATIONS } from "../theme";

export interface CodeBlockProps {
  code: string;
  language?: string;
  revealSpeed?: number;
  fontSize?: number;
  showLineNumbers?: boolean;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = "json",
  revealSpeed = 8,
  fontSize = 16,
  showLineNumbers = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Split code into lines
  const lines = useMemo(() => code.split("\n"), [code]);

  // Calculate which lines should be visible based on frame
  const visibleLines = interpolate(
    frame,
    [0, lines.length * revealSpeed],
    [0, lines.length],
    { extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        backgroundColor: COLORS.backgroundLight,
        borderRadius: RADIUS.lg,
        padding: "20px 24px",
        fontFamily: FONTS.mono,
        fontSize,
        color: COLORS.text,
        lineHeight: 1.6,
        border: `1px solid ${COLORS.telnyxGreen}30`,
        overflow: "hidden",
      }}
    >
      {/* Language badge */}
      <div
        style={{
          fontSize: 12,
          color: COLORS.telnyxGreen,
          marginBottom: 12,
          textTransform: "uppercase",
          letterSpacing: 1,
          fontWeight: 600,
        }}
      >
        {language}
      </div>

      {/* Code lines */}
      <div style={{ display: "flex", flexDirection: "column" }}>
        {lines.map((line, index) => {
          const lineOpacity = interpolate(
            visibleLines,
            [index, index + 1],
            [0, 1],
            { extrapolateRight: "clamp" }
          );

          if (lineOpacity === 0) return null;

          return (
            <div
              key={index}
              style={{
                display: "flex",
                opacity: lineOpacity,
                transform: `translateY(${interpolate(lineOpacity, [0, 1], [10, 0])}px)`,
              }}
            >
              {showLineNumbers && (
                <span
                  style={{
                    color: COLORS.textMuted,
                    minWidth: 30,
                    marginRight: 16,
                    userSelect: "none",
                  }}
                >
                  {index + 1}
                </span>
              )}
              <span
                style={{
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-all",
                }}
              >
                {line || " "}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
