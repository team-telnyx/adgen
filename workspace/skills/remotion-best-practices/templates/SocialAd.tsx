import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";
import { GlowText } from "../components/GlowText";
import { CounterAnimation } from "../components/CounterAnimation";

export interface SocialAdProps {
  /** Hook question/statement (first frame) */
  hook: string;
  /** Problem bullets to show */
  problems: string[];
  /** Solution/product name */
  solutionName: string;
  /** Key features */
  features: string[];
  /** CTA button text */
  ctaText: string;
  /** CTA URL */
  ctaUrl?: string;
  /** Highlight keyword in hook (wrapped in {green}) */
  highlightHook?: boolean;
}

const HookScene: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Parse text for {green} markers
  const parts = text.split("{green}");

  const progress = spring({
    frame,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 40,
      }}
    >
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 52,
          fontWeight: 700,
          color: COLORS.text,
          textAlign: "center",
          lineHeight: 1.3,
          opacity: progress,
          transform: `translateY(${interpolate(progress, [0, 1], [40, 0])}px)`,
        }}
      >
        {parts.map((part, i) =>
          i === 0 ? (
            part
          ) : (
            <React.Fragment key={i}>
              <span style={{ color: COLORS.telnyxGreen }}>{part}</span>
            </React.Fragment>
          )
        )}
      </div>
    </AbsoluteFill>
  );
};

const ProblemScene: React.FC<{ problems: string[] }> = ({ problems }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 40,
        gap: 24,
      }}
    >
      {problems.map((problem, i) => {
        const delay = i * 20;
        const progress = spring({
          frame: frame - delay,
          fps,
          config: SPRING_CONFIG.smooth,
        });

        return (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              opacity: progress,
              transform: `translateX(${interpolate(progress, [0, 1], [-50, 0])}px)`,
            }}
          >
            <div
              style={{
                fontSize: 28,
                opacity: 0.6,
              }}
            >
              ❌
            </div>
            <div
              style={{
                fontFamily: FONTS.sans,
                fontSize: 32,
                fontWeight: 600,
                color: COLORS.textMuted,
              }}
            >
              {problem}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const SolutionScene: React.FC<{ name: string; features: string[] }> = ({
  name,
  features,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 40,
        gap: 30,
      }}
    >
      <GlowText
        text={name}
        fontSize={56}
        delay={0}
      />

      {features.map((feature, i) => {
        const delay = 25 + i * 15;
        const progress = spring({
          frame: frame - delay,
          fps,
          config: SPRING_CONFIG.smooth,
        });

        return (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              opacity: progress,
              transform: `translateY(${interpolate(progress, [0, 1], [20, 0])}px)`,
            }}
          >
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: 14,
                backgroundColor: COLORS.telnyxGreen,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 14,
                color: COLORS.background,
                fontWeight: 700,
              }}
            >
              ✓
            </div>
            <div
              style={{
                fontFamily: FONTS.sans,
                fontSize: 26,
                fontWeight: 500,
                color: COLORS.text,
              }}
            >
              {feature}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const CTAScene: React.FC<{ text: string; url?: string }> = ({ text, url }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const ctaProgress = spring({
    frame,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  const urlProgress = spring({
    frame: frame - 20,
    fps,
    config: SPRING_CONFIG.smooth,
  });

  // Pulse animation for CTA
  const pulse = 1 + Math.sin(frame * 0.15) * 0.03;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 30,
      }}
    >
      <div
        style={{
          backgroundColor: COLORS.telnyxGreen,
          borderRadius: 32,
          padding: "20px 48px",
          color: COLORS.background,
          fontFamily: FONTS.sans,
          fontSize: 32,
          fontWeight: 700,
          transform: `scale(${interpolate(ctaProgress, [0, 1], [0.5, 1]) * pulse})`,
          opacity: ctaProgress,
          boxShadow: `0 0 40px ${COLORS.telnyxGreen}44`,
        }}
      >
        {text}
      </div>

      {url && (
        <div
          style={{
            fontFamily: FONTS.sans,
            fontSize: 22,
            fontWeight: 500,
            color: COLORS.telnyxGreen,
            opacity: urlProgress,
            letterSpacing: 1,
          }}
        >
          {url}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const SocialAd: React.FC<SocialAdProps> = ({
  hook,
  problems,
  solutionName,
  features,
  ctaText,
  ctaUrl,
}) => {
  const { fps } = useVideoConfig();

  // Scene durations (vertical 9:16 format - shorter scenes)
  const hookDur = 3 * fps;
  const problemDur = Math.max(3 * fps, problems.length * 20 + 60);
  const solutionDur = Math.max(4 * fps, features.length * 15 + 60);
  const ctaDur = 3 * fps;

  let offset = 0;
  const hookStart = offset;
  offset += hookDur;
  const problemStart = offset;
  offset += problemDur;
  const solutionStart = offset;
  offset += solutionDur;
  const ctaStart = offset;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      <Sequence from={hookStart} durationInFrames={hookDur}>
        <HookScene text={hook} />
      </Sequence>

      <Sequence from={problemStart} durationInFrames={problemDur}>
        <ProblemScene problems={problems} />
      </Sequence>

      <Sequence from={solutionStart} durationInFrames={solutionDur}>
        <SolutionScene name={solutionName} features={features} />
      </Sequence>

      <Sequence from={ctaStart} durationInFrames={ctaDur}>
        <CTAScene text={ctaText} url={ctaUrl} />
      </Sequence>
    </AbsoluteFill>
  );
};
