import { spring, interpolate, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { Series, AbsoluteFill } from "remotion";
import { ReactNode } from "react";
import { StatReveal } from "../components/StatReveal";
import { FloatingCard } from "../components/FloatingCard";
import { GradientMesh } from "../components/GradientMesh";
import { RisingShapes } from "../components/RisingShapes";
import { TextCut } from "../components/TextCut";
import { ClipReveal } from "../components/ClipReveal";

export interface CleanProductPromoProps {
  hookTexts: string[];
  hookFramesPerText?: number;
  stats: { value: string; label: string }[];
  badges: string[];
  uiCard?: ReactNode;
  gradientColors?: [string, string];
  valueWords: string[];
  ctaUrl: string;
  ctaSubtext?: string;
  accentColor?: string;
}

const FONTS = {
  serif: '"Georgia", "Times New Roman", serif',
  sans: '"Inter", system-ui, sans-serif',
};

const HookScene: React.FC<{ texts: string[]; framesPerText: number }> = ({ texts, framesPerText }) => (
  <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#FFFFFF" }}>
    <TextCut texts={texts} frameDuration={framesPerText} />
  </AbsoluteFill>
);

const StatsScene: React.FC<{ stats: { value: string; label: string }[] }> = ({ stats }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", backgroundColor: "#FFFFFF", gap: 40 }}>
      {stats.map((stat, i) => <StatReveal key={i} {...stat} delay={i * 25} />)}
    </AbsoluteFill>
  );
};

const BadgesScene: React.FC<{ badges: string[] }> = ({ badges }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#f1f1f1", gap: 24 }}>
      {badges.map((badge, i) => {
        const progress = spring({ frame: frame - i * 10, fps, config: { damping: 14, stiffness: 80 } });
        return (
          <div key={badge} style={{ padding: "16px 32px", backgroundColor: "#FFFFFF", borderRadius: 100, boxShadow: "0 4px 20px rgba(0,0,0,0.08)", transform: `translateY(${interpolate(progress, [0, 1], [100, 0])}px)`, opacity: progress }}>
            <span style={{ fontFamily: FONTS.sans, fontSize: 20, fontWeight: 600, color: "#000000" }}>{badge}</span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const UIPreviewScene: React.FC<{ uiCard?: ReactNode; gradientColors: [string, string] }> = ({ uiCard, gradientColors }) => (
  <GradientMesh colors={gradientColors}>
    <FloatingCard delay={0} direction="right" shadowIntensity="medium">{uiCard}</FloatingCard>
  </GradientMesh>
);

const ValuePropScene: React.FC<{ words: string[] }> = ({ words }) => (
  <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "#FFFFFF", gap: 24 }}>
    {words.map((word, i) => (
      <ClipReveal key={i} delay={i * 20}>
        <span style={{ fontFamily: FONTS.serif, fontSize: 64, color: "#000000", fontWeight: 400 }}>
          {word}
        </span>
      </ClipReveal>
    ))}
  </AbsoluteFill>
);

const CTAScene: React.FC<{ url: string; subtext?: string; accentColor: string }> = ({ url, subtext, accentColor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - 10, fps, config: { damping: 15, stiffness: 80 } });
  const underlineWidth = interpolate(frame, [25, 55], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", backgroundColor: "#FFFFFF", overflow: "hidden" }}>
      <RisingShapes positions={[280, 440, 560, 700]} color={accentColor} />
      <div style={{ position: "relative", zIndex: 1, textAlign: "center" }}>
        <div style={{ fontFamily: FONTS.sans, fontSize: 52, fontWeight: 700, color: "#000000", opacity: progress, transform: `translateY(${(1 - progress) * 30}px)` }}>{url}</div>
        <div style={{ width: `${underlineWidth}%`, height: 4, backgroundColor: accentColor, margin: "12px auto 0", borderRadius: 2 }} />
        {subtext && <div style={{ fontFamily: FONTS.sans, fontSize: 18, color: "#666666", marginTop: 16, opacity: interpolate(frame, [30, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{subtext}</div>}
      </div>
    </AbsoluteFill>
  );
};

export const CleanProductPromo: React.FC<CleanProductPromoProps> = ({ hookTexts, hookFramesPerText = 45, stats, badges, uiCard, gradientColors = ["#1a2332", "#0d3d2e"], valueWords, ctaUrl, ctaSubtext, accentColor = "#00E3AA" }) => (
  <Series>
    <Series.Sequence durationInFrames={hookTexts.length * hookFramesPerText}><HookScene texts={hookTexts} framesPerText={hookFramesPerText} /></Series.Sequence>
    <Series.Sequence durationInFrames={120}><StatsScene stats={stats} /></Series.Sequence>
    <Series.Sequence durationInFrames={90}><BadgesScene badges={badges} /></Series.Sequence>
    {uiCard && <Series.Sequence durationInFrames={120}><UIPreviewScene uiCard={uiCard} gradientColors={gradientColors} /></Series.Sequence>}
    <Series.Sequence durationInFrames={90}><ValuePropScene words={valueWords} /></Series.Sequence>
    <Series.Sequence durationInFrames={90}><CTAScene url={ctaUrl} subtext={ctaSubtext} accentColor={accentColor} /></Series.Sequence>
  </Series>
);
