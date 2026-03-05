import { interpolate, Easing, useCurrentFrame } from "remotion";

export interface RisingShapesProps {
  count?: number;
  color?: string;
  opacity?: number;
  positions?: number[];
  pillWidth?: number;
  pillHeight?: number;
}

export const RisingShapes: React.FC<RisingShapesProps> = ({
  count = 4,
  color = "#00E3AA",
  opacity = 0.12,
  positions = [280, 440, 560, 700],
  pillWidth = 80,
  pillHeight = 300,
}) => {
  const frame = useCurrentFrame();

  return (
    <>
      {Array.from({ length: count }).map((_, i) => {
        const rise = interpolate(
          frame,
          [i * 5, i * 5 + 60],
          [120, -20],
          { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              bottom: `${rise}%`,
              left: positions[i % positions.length],
              width: pillWidth,
              height: pillHeight,
              borderRadius: pillWidth / 2,
              backgroundColor: color,
              opacity,
            }}
          />
        );
      })}
    </>
  );
};
