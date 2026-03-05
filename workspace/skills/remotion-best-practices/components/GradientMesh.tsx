import { interpolate, useCurrentFrame } from "remotion";
import { ReactNode } from "react";

export interface GradientMeshProps {
  children?: ReactNode;
  colors?: [string, string];
  style?: "radial" | "linear";
  animate?: boolean;
}

export const GradientMesh: React.FC<GradientMeshProps> = ({
  children,
  colors = ["#1a2332", "#0d3d2e"],
  style = "radial",
  animate = false,
}) => {
  const frame = useCurrentFrame();

  const shift = animate ? interpolate(frame, [0, 100], [0, 10]) : 0;
  const [start, end] = colors;

  const background =
    style === "radial"
      ? `radial-gradient(ellipse at ${30 + shift}% ${20 + shift}%, ${start} 0%, ${end} 100%)`
      : `linear-gradient(${135 + shift}deg, ${start} 0%, ${end} 100%)`;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background,
      }}
    >
      {children}
    </div>
  );
};
