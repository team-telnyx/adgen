import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
  OffthreadVideo,
  staticFile,
} from "remotion";
import { COLORS, FONTS, SPRING_CONFIG } from "../theme";
import { PhoneFrame } from "../components/PhoneFrame";

export interface PhoneScreenDemoProps {
  /** Video source path (relative to public folder or URL) */
  videoSrc: string;
  /** Caption text below phone */
  caption?: string;
  /** Badge text at top (e.g., "Real phone call") */
  badge?: string;
  /** Phone frame color */
  frameColor?: string;
  /** Phone width in pixels */
  phoneWidth?: number;
  /** Intro text before showing phone */
  introText?: string;
  /** Duration of intro in frames */
  introDuration?: number;
  /** Outro text after video */
  outroText?: string;
  /** Duration of outro in frames */
  outroDuration?: number;
}

const IntroScene: React.FC<{ text: string; duration: number }> = ({
  text,
  duration,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    config: SPRING_CONFIG.smooth,
  });

  const fadeOut = interpolate(
    frame,
    [duration - 20, duration],
    [1, 0],
    { extrapolateLeft: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeOut,
      }}
    >
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 56,
          fontWeight: 700,
          color: COLORS.text,
          textAlign: "center",
          opacity: progress,
          transform: `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`,
          padding: "0 60px",
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

const OutroScene: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    config: SPRING_CONFIG.smooth,
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 48,
          fontWeight: 700,
          color: COLORS.telnyxGreen,
          textAlign: "center",
          opacity: progress,
          transform: `scale(${interpolate(progress, [0, 1], [0.8, 1])})`,
          padding: "0 60px",
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

const Badge: React.FC<{ text: string; delay: number }> = ({ text, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 60,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [-20, 0])}px)`,
      }}
    >
      <div
        style={{
          backgroundColor: COLORS.telnyxGreen,
          borderRadius: 24,
          padding: "12px 24px",
          color: COLORS.background,
          fontWeight: 700,
          fontSize: 18,
          fontFamily: FONTS.sans,
        }}
      >
        {text}
      </div>
    </div>
  );
};

export const PhoneScreenDemo: React.FC<PhoneScreenDemoProps> = ({
  videoSrc,
  caption,
  badge,
  frameColor = "#1a1a1a",
  phoneWidth = 300,
  introText,
  introDuration = 90,
  outroText,
  outroDuration = 90,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const phoneProgress = spring({
    frame: introText ? frame - introDuration : frame,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  // Calculate timing
  const introEnd = introText ? introDuration : 0;
  const outroStart = outroText ? durationInFrames - outroDuration : durationInFrames;
  const videoEnd = outroText ? outroStart : durationInFrames;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {/* Intro */}
      {introText && (
        <Sequence from={0} durationInFrames={introDuration}>
          <IntroScene text={introText} duration={introDuration} />
        </Sequence>
      )}

      {/* Main phone demo */}
      <Sequence from={introEnd} durationInFrames={videoEnd - introEnd}>
        <AbsoluteFill
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 40,
          }}
        >
          {badge && <Badge text={badge} delay={30} />}

          <div
            style={{
              transform: `scale(${interpolate(phoneProgress, [0, 1], [0.8, 1])})`,
              opacity: phoneProgress,
            }}
          >
            <PhoneFrame frameColor={frameColor} width={phoneWidth}>
              <OffthreadVideo
                src={videoSrc.startsWith("http") ? videoSrc : staticFile(videoSrc)}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </PhoneFrame>
          </div>

          {caption && (
            <div
              style={{
                fontFamily: FONTS.sans,
                fontSize: 24,
                color: COLORS.textMuted,
                textAlign: "center",
                opacity: interpolate(phoneProgress, [0, 1], [0, 0.7]),
                padding: "0 40px",
              }}
            >
              {caption}
            </div>
          )}
        </AbsoluteFill>
      </Sequence>

      {/* Outro */}
      {outroText && (
        <Sequence from={outroStart} durationInFrames={outroDuration}>
          <OutroScene text={outroText} />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
