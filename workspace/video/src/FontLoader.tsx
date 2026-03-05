import React from "react";
import { AbsoluteFill, staticFile } from "remotion";

const fontStyles = `
@font-face {
  font-family: "PP Formula";
  src: url("${staticFile("fonts/PPFormula-Extrabold.otf")}") format("opentype");
  font-weight: 800;
  font-style: normal;
}
@font-face {
  font-family: "Inter";
  src: url("${staticFile("fonts/Inter-Regular.ttf")}") format("truetype");
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: "Inter";
  src: url("${staticFile("fonts/Inter-Medium.ttf")}") format("truetype");
  font-weight: 500;
  font-style: normal;
}
@font-face {
  font-family: "Inter";
  src: url("${staticFile("fonts/Inter-Bold.ttf")}") format("truetype");
  font-weight: 700;
  font-style: normal;
}
`;

export const FontLoader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill>
    <style dangerouslySetInnerHTML={{ __html: fontStyles }} />
    {children}
  </AbsoluteFill>
);
