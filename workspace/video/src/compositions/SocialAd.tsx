import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";
import { FontLoader } from "../FontLoader";

export interface SocialAdProps {
  headline: string;
  subhead?: string;
  cta?: string;
  heroImage?: string;
  accentColor?: string;
  format?: "landscape" | "square" | "vertical";
}

// Scene 1: Bold headline slam (0-3s)
const HeadlineSlam: React.FC<{ text: string; accent: string }> = ({
  text,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const scale = interpolate(prog, [0, 1], [1.3, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          fontFamily: FONTS.heading,
          fontSize: 80,
          fontWeight: 800,
          color: accent,
          textAlign: "center",
          maxWidth: "85%",
          lineHeight: 1.1,
          opacity: prog,
          transform: `scale(${scale})`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

// Scene 2: Subhead flash (3-5s)
const SubheadFlash: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.smooth });
  const y = interpolate(prog, [0, 1], [30, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 32,
          fontWeight: 500,
          color: COLORS.cream,
          textAlign: "center",
          maxWidth: "80%",
          opacity: prog,
          transform: `translateY(${y}px)`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

// Scene 3: CTA pulse (5-7s)
const CTAPulse: React.FC<{ cta: string; accent: string }> = ({ cta, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const pulse = 1 + Math.sin(frame * 0.18) * 0.04;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          backgroundColor: accent,
          borderRadius: 32,
          padding: "20px 48px",
          fontFamily: FONTS.heading,
          fontSize: 36,
          fontWeight: 800,
          color: COLORS.black,
          opacity: prog,
          transform: `scale(${interpolate(prog, [0, 1], [0.5, 1]) * pulse})`,
          boxShadow: `0 0 40px ${accent}55`,
        }}
      >
        {cta}
      </div>
    </AbsoluteFill>
  );
};

export const SocialAd: React.FC<SocialAdProps> = ({
  headline,
  subhead = "",
  cta = "Learn More",
  accentColor = COLORS.citron,
  format = "square",
}) => {
  const { fps } = useVideoConfig();
  // 7 seconds: headline 3s, subhead 2s, cta 2s
  const headDur = 3 * fps;
  const subDur = subhead ? 2 * fps : 0;
  const ctaDur = 2 * fps;

  let offset = 0;
  return (
    <FontLoader>
      <AbsoluteFill style={{ backgroundColor: COLORS.black }}>
        <Sequence from={offset} durationInFrames={headDur}>
          <HeadlineSlam text={headline} accent={accentColor} />
        </Sequence>
        {subhead && (
          <Sequence from={(offset += headDur)} durationInFrames={subDur}>
            <SubheadFlash text={subhead} />
          </Sequence>
        )}
        <Sequence
          from={subhead ? (offset += subDur) : (offset += headDur)}
          durationInFrames={ctaDur}
        >
          <CTAPulse cta={cta} accent={accentColor} />
        </Sequence>
      </AbsoluteFill>
    </FontLoader>
  );
};

export default SocialAd;
