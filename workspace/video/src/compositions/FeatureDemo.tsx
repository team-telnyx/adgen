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

export interface FeatureDemoProps {
  headline: string;
  subhead?: string;
  cta?: string;
  heroImage?: string;
  accentColor?: string;
  format?: "landscape" | "square" | "vertical";
  /** Up to 3 features: { icon, title, desc } */
  features?: Array<{ icon: string; title: string; desc: string }>;
}

const DEFAULT_FEATURES = [
  { icon: "⚡", title: "Feature One", desc: "Description of the first feature" },
  { icon: "🔒", title: "Feature Two", desc: "Description of the second feature" },
  { icon: "🚀", title: "Feature Three", desc: "Description of the third feature" },
];

// Scene 1: Hook headline (0-4s)
const HookScene: React.FC<{ headline: string; accent: string }> = ({
  headline,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.bouncy });

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
          fontSize: 64,
          fontWeight: 800,
          color: COLORS.white,
          textAlign: "center",
          maxWidth: "80%",
          lineHeight: 1.2,
          opacity: prog,
          transform: `scale(${interpolate(prog, [0, 1], [0.9, 1])})`,
        }}
      >
        {headline}
      </div>
    </AbsoluteFill>
  );
};

// Scene 2-4: Individual feature panels (4s each)
const FeaturePanel: React.FC<{
  icon: string;
  title: string;
  desc: string;
  accent: string;
}> = ({ icon, title, desc, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconProg = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const textProg = spring({
    frame: Math.max(0, frame - 10),
    fps,
    config: SPRING_CONFIG.smooth,
  });
  const descProg = spring({
    frame: Math.max(0, frame - 20),
    fps,
    config: SPRING_CONFIG.smooth,
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        display: "flex",
        gap: 20,
      }}
    >
      {/* Accent bar */}
      <div
        style={{
          width: 60,
          height: 4,
          backgroundColor: accent,
          borderRadius: 2,
          marginBottom: 10,
          opacity: iconProg,
        }}
      />
      <div
        style={{
          fontSize: 64,
          opacity: iconProg,
          transform: `scale(${interpolate(iconProg, [0, 1], [0.3, 1])})`,
        }}
      >
        {icon}
      </div>
      <div
        style={{
          fontFamily: FONTS.heading,
          fontSize: 48,
          fontWeight: 800,
          color: COLORS.white,
          opacity: textProg,
          transform: `translateY(${interpolate(textProg, [0, 1], [20, 0])}px)`,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 24,
          fontWeight: 400,
          color: COLORS.textMuted,
          textAlign: "center",
          maxWidth: "65%",
          opacity: descProg,
          transform: `translateY(${interpolate(descProg, [0, 1], [15, 0])}px)`,
        }}
      >
        {desc}
      </div>
    </AbsoluteFill>
  );
};

// Scene 5: CTA (16-18s)
const CTAScene: React.FC<{ cta: string; subhead: string; accent: string }> = ({
  cta,
  subhead,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const pulse = 1 + Math.sin(frame * 0.15) * 0.03;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        display: "flex",
        gap: 24,
      }}
    >
      {subhead && (
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
      )}
      <div
        style={{
          backgroundColor: accent,
          borderRadius: 36,
          padding: "22px 52px",
          fontFamily: FONTS.heading,
          fontSize: 38,
          fontWeight: 800,
          color: COLORS.black,
          opacity: prog,
          transform: `scale(${interpolate(prog, [0, 1], [0.5, 1]) * pulse})`,
          boxShadow: `0 0 50px ${accent}55`,
        }}
      >
        {cta}
      </div>
    </AbsoluteFill>
  );
};

export const FeatureDemo: React.FC<FeatureDemoProps> = ({
  headline,
  subhead = "",
  cta = "Get Started",
  accentColor = COLORS.green,
  format = "landscape",
  features,
}) => {
  const { fps } = useVideoConfig();
  const feats = (features && features.length > 0) ? features.slice(0, 3) : DEFAULT_FEATURES;

  // 18 seconds: hook 4s, 3 features × 4s, cta 2s
  const hookDur = 4 * fps;
  const featDur = 4 * fps;
  const ctaDur = 2 * fps;

  let offset = 0;
  return (
    <FontLoader>
      <AbsoluteFill style={{ backgroundColor: COLORS.black }}>
        <Sequence from={offset} durationInFrames={hookDur}>
          <HookScene headline={headline} accent={accentColor} />
        </Sequence>
        {feats.map((f, i) => (
          <Sequence
            key={i}
            from={(offset = hookDur + i * featDur)}
            durationInFrames={featDur}
          >
            <FeaturePanel
              icon={f.icon}
              title={f.title}
              desc={f.desc}
              accent={accentColor}
            />
          </Sequence>
        ))}
        <Sequence
          from={hookDur + feats.length * featDur}
          durationInFrames={ctaDur}
        >
          <CTAScene cta={cta} subhead={subhead} accent={accentColor} />
        </Sequence>
      </AbsoluteFill>
    </FontLoader>
  );
};

export default FeatureDemo;
