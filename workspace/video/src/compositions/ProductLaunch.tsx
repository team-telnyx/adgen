import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Img,
} from "remotion";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";
import { FontLoader } from "../FontLoader";

export interface ProductLaunchProps {
  headline: string;
  subhead?: string;
  cta?: string;
  heroImage?: string;
  accentColor?: string;
  format?: "landscape" | "square" | "vertical";
}

// Scene: Accent glow background
const GlowBg: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const pulse = 0.4 + Math.sin(frame * 0.04) * 0.15;
  return (
    <div
      style={{
        position: "absolute",
        top: "30%",
        left: "50%",
        width: 600,
        height: 600,
        borderRadius: "50%",
        background: color,
        opacity: pulse,
        filter: "blur(180px)",
        transform: "translate(-50%, -50%)",
      }}
    />
  );
};

// Scene 1: Hook — "Why Now" (0-3s)
const HookScene: React.FC<{ headline: string; accent: string }> = ({
  headline,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const scale = interpolate(prog, [0, 1], [0.85, 1]);
  const opacity = interpolate(prog, [0, 1], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.black,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <GlowBg color={accent} />
      <div
        style={{
          fontFamily: FONTS.heading,
          fontSize: 72,
          fontWeight: 800,
          color: COLORS.white,
          textAlign: "center",
          maxWidth: "80%",
          lineHeight: 1.15,
          opacity,
          transform: `scale(${scale})`,
          zIndex: 1,
        }}
      >
        {headline}
      </div>
    </AbsoluteFill>
  );
};

// Scene 2: Subhead — "What Changes" (3-6s)
const SubheadScene: React.FC<{ subhead: string }> = ({ subhead }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.smooth });
  const y = interpolate(prog, [0, 1], [40, 0]);

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
          fontSize: 36,
          fontWeight: 500,
          color: COLORS.cream,
          textAlign: "center",
          maxWidth: "75%",
          lineHeight: 1.5,
          opacity: prog,
          transform: `translateY(${y}px)`,
        }}
      >
        {subhead}
      </div>
    </AbsoluteFill>
  );
};

// Scene 3: Hero image — "How It Works" (6-11s)
const HeroScene: React.FC<{ heroImage: string; accent: string }> = ({
  heroImage,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.gentle });
  const zoom = interpolate(frame, [0, 150], [1, 1.06], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{ backgroundColor: COLORS.black, justifyContent: "center", alignItems: "center" }}
    >
      <GlowBg color={accent} />
      <div
        style={{
          opacity: prog,
          transform: `scale(${zoom})`,
          width: "75%",
          maxHeight: "80%",
          overflow: "hidden",
          borderRadius: 16,
          zIndex: 1,
        }}
      >
        <Img
          src={heroImage}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>
    </AbsoluteFill>
  );
};

// Scene 4: CTA — "Next Steps" (11-15s)
const CTAScene: React.FC<{ cta: string; accent: string }> = ({ cta, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prog = spring({ frame, fps, config: SPRING_CONFIG.bouncy });
  const pulse = 1 + Math.sin(frame * 0.15) * 0.03;

  return (
    <AbsoluteFill
      style={{ backgroundColor: COLORS.black, justifyContent: "center", alignItems: "center" }}
    >
      <div
        style={{
          backgroundColor: accent,
          borderRadius: 40,
          padding: "24px 56px",
          fontFamily: FONTS.heading,
          fontSize: 40,
          fontWeight: 800,
          color: COLORS.black,
          opacity: prog,
          transform: `scale(${interpolate(prog, [0, 1], [0.6, 1]) * pulse})`,
          boxShadow: `0 0 60px ${accent}66`,
        }}
      >
        {cta}
      </div>
    </AbsoluteFill>
  );
};

export const ProductLaunch: React.FC<ProductLaunchProps> = ({
  headline,
  subhead = "",
  cta = "Learn More",
  heroImage = "",
  accentColor = COLORS.green,
  format = "landscape",
}) => {
  const { fps } = useVideoConfig();
  // 15 seconds total: hook 3s, subhead 3s, hero 5s, cta 4s
  const hookDur = 3 * fps;
  const subDur = 3 * fps;
  const heroDur = 5 * fps;
  const ctaDur = 4 * fps;

  let offset = 0;
  return (
    <FontLoader>
      <AbsoluteFill style={{ backgroundColor: COLORS.black }}>
        <Sequence from={(offset)} durationInFrames={hookDur}>
          <HookScene headline={headline} accent={accentColor} />
        </Sequence>
        <Sequence from={(offset += hookDur)} durationInFrames={subDur}>
          <SubheadScene subhead={subhead} />
        </Sequence>
        {heroImage && (
          <Sequence from={(offset += subDur)} durationInFrames={heroDur}>
            <HeroScene heroImage={heroImage} accent={accentColor} />
          </Sequence>
        )}
        <Sequence
          from={heroImage ? (offset += heroDur) : (offset += subDur)}
          durationInFrames={ctaDur}
        >
          <CTAScene cta={cta} accent={accentColor} />
        </Sequence>
      </AbsoluteFill>
    </FontLoader>
  );
};

export default ProductLaunch;
