import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";

export interface HowItWorksStep { title: string; description: string; icon?: string; }
export interface HowItWorksProps { productName: string; steps: HowItWorksStep[]; ctaText?: string; }

const StepCard: React.FC<{ step: HowItWorksStep; index: number; active: boolean; past: boolean }> = ({ step, index, active, past }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - 20 - index * 45, fps, config: SPRING_CONFIG.bouncy });
  const border = active ? COLORS.telnyxGreen : past ? COLORS.telnyxGreenDim : "#1E1E1E";
  return (
    <div style={{ width: 280, background: active ? COLORS.telnyxGreenDim : "#111", border: `2px solid ${border}`, borderRadius: 16, padding: "24px 20px", transform: `scale(${interpolate(p, [0, 1], [0.8, 1])})`, opacity: interpolate(p, [0, 0.5], [0, 1]), boxShadow: active ? "0 0 30px rgba(0, 227, 170, 0.15)" : "none" }}>
      <div style={{ fontFamily: FONTS.mono, fontSize: 13, fontWeight: 700, color: active ? COLORS.telnyxGreen : "#444", textTransform: "uppercase", letterSpacing: 1 }}>{past ? "✓" : `Step ${index + 1}`}</div>
      {step.icon && <div style={{ fontSize: 36, marginTop: 4 }}>{step.icon}</div>}
      <div style={{ fontFamily: FONTS.sans, fontSize: 20, fontWeight: 700, color: COLORS.text, marginTop: 8 }}>{step.title}</div>
      <div style={{ fontFamily: FONTS.sans, fontSize: 14, color: "#888", lineHeight: 1.5, marginTop: 8 }}>{step.description}</div>
    </div>
  );
};

export const HowItWorks: React.FC<HowItWorksProps> = ({ productName, steps, ctaText = "Get Started" }) => {
  const frame = useCurrentFrame();
  const stepDur = 45;
  const totalSteps = steps.length;
  const activeIdx = Math.min(Math.floor(frame / stepDur), totalSteps - 1);
  const inCta = frame >= totalSteps * stepDur;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background, fontFamily: FONTS.sans, justifyContent: "center", alignItems: "center", padding: "40px 20px" }}>
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <AnimatedText text={`How ${productName} Works`} delay={0} fontSize={42} fontWeight={700} color={COLORS.text} />
        <AnimatedText text="Simple steps to get started" delay={20} fontSize={18} color="#666" style={{ marginTop: 8 }} />
      </div>
      {!inCta && <div style={{ display: "flex", gap: 20, flexWrap: "wrap", justifyContent: "center" }}>{steps.map((s, i) => <StepCard key={i} step={s} index={i} active={i === activeIdx} past={i < activeIdx} />)}</div>}
      {inCta && <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}><AnimatedText text="Ready to get started?" delay={totalSteps * stepDur} fontSize={28} fontWeight={600} color={COLORS.text} /><div style={{ background: COLORS.telnyxGreen, color: "#000", fontFamily: FONTS.sans, fontSize: 18, fontWeight: 600, padding: "14px 36px", borderRadius: 8 }}>{ctaText}</div></div>}
      <div style={{ position: "absolute", bottom: 30, display: "flex", gap: 8 }}>{[...Array(totalSteps + 1)].map((_, i) => <div key={i} style={{ width: i < totalSteps ? 24 : 8, height: 8, borderRadius: 4, background: frame >= i * stepDur + stepDur * 0.5 ? COLORS.telnyxGreen : "#333" }} />)}</div>
    </AbsoluteFill>
  );
};
