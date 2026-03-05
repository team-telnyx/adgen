import { spring, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface StatRevealProps {
  value: string;
  label: string;
  delay?: number;
  fontSize?: number;
  labelFontSize?: number;
  fontFamily?: string;
  color?: string;
  labelColor?: string;
}

export const StatReveal: React.FC<StatRevealProps> = ({
  value,
  label,
  delay = 0,
  fontSize = 100,
  labelFontSize = 24,
  fontFamily = '"Georgia", "Times New Roman", serif',
  color = "#000000",
  labelColor = "#666666",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const y = interpolate(progress, [0, 1], [60, 0]);
  const opacity = progress;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        transform: `translateY(${y}px)`,
        opacity,
      }}
    >
      <span
        style={{
          fontFamily,
          fontSize,
          color,
          fontWeight: 400,
          lineHeight: 1,
        }}
      >
        {value}
      </span>
      <span
        style={{
          fontFamily: '"Inter", system-ui, sans-serif',
          fontSize: labelFontSize,
          color: labelColor,
          marginTop: 8,
        }}
      >
        {label}
      </span>
    </div>
  );
};
