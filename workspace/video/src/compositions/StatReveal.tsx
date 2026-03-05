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

export interface StatRevealProps {
  headline: string; // e.g. "40%"
  subhead?: string; // e.g. "reduction in wait times"
  cta?: string;
  heroImage?: string;
  accentColor?: string;
  format?: "landscape" | "square" | "vertical";
}

// Parse numeric value from headline (e.g. "40%" → 40, "$1.2M" → 1.2)
function parseTarget(s: string): { prefix: string; value: number; suffix: string } {
  const match = s.match(/^([^0-9]*?)([\d.]+)(.*)$/);
  if (!match) return { prefix: "", value: 0, suffix: s };
  return { prefix: match[1], value: parseFloat(match[2]), suffix: match[3] };
}

// Scene 1: Counter animation (0-6s)
const CounterScene: React.FC<{ headline: string; accent: string }> = ({
  headline,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { prefix, value, suffix } = parseTarget(headline);

  const countDur = 4 * fps;
  const rawProg = interpolate(frame, [0, countDur], [0, 1], {
    extrapolateRight: "clamp",
  });
  // Ease-out cubic
  const eased = 1 - Math.pow(1 - rawProg, 3);
  const current = eased * value;

  const popScale = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const scale = interpolate(popScale, [0, 1], [0.5, 1]);

  // Determine decimal places from original
  const decimals = value % 1 !== 0 ? 1 : 0;

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
          fontSize: 120,
          fontWeight: 800,
          color: accent,
          transform: `scale(${scale})`,
          textShadow: `0 0 30px ${accent}55, 0 0 60px ${accent}33`,
        }}
      >
        {prefix}
        {current.toFixed(decimals)}
        {suffix}
      </div>
    </AbsoluteFill>
  );
};

// Scene 2: Supporting text (6-8s)
const LabelScene: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.smooth });
  const y = interpolate(prog, [0, 1], [20, 0]);

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
          maxWidth: "75%",
          opacity: prog,
          transform: `translateY(${y}px)`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

// Scene 3: CTA hold (8-10s)
const CTAHold: React.FC<{ headline: string; subhead: string; cta: string; accent: string }> = ({
  headline,
  subhead,
  cta,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.smooth });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
        gap: 20,
        flexDirection: "column",
        display: "flex",
      }}
    >
      <div
        style={{
          fontFamily: FONTS.heading,
          fontSize: 80,
          fontWeight: 800,
          color: accent,
        }}
      >
        {headline}
      </div>
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 28,
          color: COLORS.cream,
          opacity: prog,
        }}
      >
        {subhead}
      </div>
      {cta && (
        <div
          style={{
            marginTop: 20,
            backgroundColor: accent,
            borderRadius: 28,
            padding: "16px 40px",
            fontFamily: FONTS.sans,
            fontSize: 24,
            fontWeight: 700,
            color: COLORS.black,
            opacity: prog,
          }}
        >
          {cta}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const StatReveal: React.FC<StatRevealProps> = ({
  headline,
  subhead = "",
  cta = "",
  accentColor = COLORS.green,
  format = "landscape",
}) => {
  const { fps } = useVideoConfig();
  // 10 seconds: counter 6s, label 2s, cta hold 2s
  const counterDur = 6 * fps;
  const labelDur = 2 * fps;
  const ctaDur = 2 * fps;

  return (
    <FontLoader>
      <AbsoluteFill style={{ backgroundColor: COLORS.black }}>
        <Sequence from={0} durationInFrames={counterDur}>
          <CounterScene headline={headline} accent={accentColor} />
        </Sequence>
        <Sequence from={counterDur} durationInFrames={labelDur}>
          <LabelScene text={subhead} />
        </Sequence>
        <Sequence from={counterDur + labelDur} durationInFrames={ctaDur}>
          <CTAHold
            headline={headline}
            subhead={subhead}
            cta={cta}
            accent={accentColor}
          />
        </Sequence>
      </AbsoluteFill>
    </FontLoader>
  );
};

export default StatReveal;
