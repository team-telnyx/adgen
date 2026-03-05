import { spring, interpolate, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { Series } from "remotion";

const COLORS = {
  bg: "#FFFFFF",
  bgLight: "#f1f1f1",
  text: "#000000",
  textMuted: "#666666",
  green: "#00E3AA",
  greenDim: "rgba(0, 227, 170, 0.15)",
  gradientStart: "#1a2332",
  gradientEnd: "#0d3d2e",
};

const FONTS = {
  serif: '"Georgia", "Times New Roman", serif',
  sans: '"Inter", system-ui, sans-serif',
};

// Scene 1: Hook - Simple text cut
const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const firstText = frame < 45 ? "Every voice." : "Every language.";

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: COLORS.bg,
      }}
    >
      <h1
        style={{
          fontFamily: FONTS.serif,
          fontSize: 120,
          color: COLORS.text,
          margin: 0,
          fontWeight: 400,
        }}
      >
        {firstText}
      </h1>
    </div>
  );
};

// Scene 2: Stats with spring animation
const StatsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const stats = [
    { value: "2,015", label: "voices" },
    { value: "89", label: "languages" },
    { value: "181", label: "accents" },
  ];

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: COLORS.bg,
        gap: 40,
      }}
    >
      {stats.map((stat, i) => {
        const delay = i * 25;
        const progress = spring({
          frame: frame - delay,
          fps,
          config: { damping: 12, stiffness: 100 },
        });
        const y = interpolate(progress, [0, 1], [60, 0]);
        const opacity = progress;

        return (
          <div
            key={i}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transform: `translateY(${y}px)`,
              opacity,
            }}
          >
            <span
              style={{
                fontFamily: FONTS.serif,
                fontSize: 100,
                color: COLORS.text,
                fontWeight: 400,
                lineHeight: 1,
              }}
            >
              {stat.value}
            </span>
            <span
              style={{
                fontFamily: FONTS.sans,
                fontSize: 24,
                color: COLORS.textMuted,
                marginTop: 8,
              }}
            >
              {stat.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};

// Scene 3: Provider badges
const ProvidersScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const providers = ["Azure", "AWS", "MiniMax", "Telnyx"];

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: COLORS.bgLight,
        gap: 24,
      }}
    >
      {providers.map((provider, i) => {
        const delay = i * 10;
        const progress = spring({
          frame: frame - delay,
          fps,
          config: { damping: 14, stiffness: 80 },
        });
        const y = interpolate(progress, [0, 1], [100, 0]);
        const opacity = progress;

        return (
          <div
            key={provider}
            style={{
              padding: "16px 32px",
              backgroundColor: COLORS.bg,
              borderRadius: 100,
              boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
              transform: `translateY(${y}px)`,
              opacity,
            }}
          >
            <span
              style={{
                fontFamily: FONTS.sans,
                fontSize: 20,
                fontWeight: 600,
                color: COLORS.text,
              }}
            >
              {provider}
            </span>
          </div>
        );
      })}
    </div>
  );
};

// Scene 4: UI Preview with gradient
const UIPreviewScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideProgress = interpolate(
    frame,
    [0, 30],
    [1, 0],
    { easing: Easing.out(Easing.cubic) }
  );

  const x = slideProgress * 300;
  const rotate = slideProgress * 5;
  const opacity = interpolate(frame, [0, 15], [0, 1]);

  const typeChars = Math.min(Math.floor((frame - 30) / 2), 35);
  const typeText = "English (US) - Neutral accent".slice(0, typeChars);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: `radial-gradient(ellipse at 30% 20%, ${COLORS.gradientStart} 0%, ${COLORS.gradientEnd} 100%)`,
      }}
    >
      <div
        style={{
          width: 400,
          padding: 32,
          backgroundColor: COLORS.bg,
          borderRadius: 16,
          boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
          transform: `translateX(${x}px) rotate(${rotate}deg)`,
          opacity,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "50%",
              backgroundColor: COLORS.greenDim,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <div
              style={{
                width: 16,
                height: 16,
                borderLeft: `4px solid ${COLORS.green}`,
                borderBottom: `4px solid ${COLORS.green}`,
                transform: "rotate(-45deg) translate(2px, -2px)",
              }}
            />
          </div>
          <div>
            <div
              style={{
                fontFamily: FONTS.sans,
                fontSize: 18,
                fontWeight: 600,
                color: COLORS.text,
              }}
            >
              Emma
            </div>
            <div
              style={{
                fontFamily: FONTS.sans,
                fontSize: 14,
                color: COLORS.textMuted,
                marginTop: 4,
              }}
            >
              {typeText}
              <span style={{ animation: "blink 1s infinite" }}>|</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Scene 5: Value Prop with text reveal
const ValuePropScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = ["Compare.", "Listen.", "Choose."];

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: COLORS.bg,
        gap: 24,
      }}
    >
      {words.map((word, i) => {
        const delay = i * 20;
        const progress = spring({
          frame: frame - delay,
          fps,
          config: { damping: 15, stiffness: 100 },
        });

        return (
          <span
            key={i}
            style={{
              fontFamily: FONTS.serif,
              fontSize: 64,
              color: COLORS.text,
              fontWeight: 400,
              clipPath: `inset(0 ${100 - progress * 100}% 0 0)`,
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

// Scene 6: CTA with rising pill shapes
const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pills = [0, 1, 2, 3];
  const positions = [280, 440, 560, 700];

  const urlProgress = spring({
    frame: frame - 10,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  const underlineWidth = interpolate(
    frame,
    [25, 55],
    [0, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }
  );

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: COLORS.bg,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {pills.map((_, i) => {
        const rise = interpolate(
          frame,
          [i * 5, i * 5 + 60],
          [120, -20],
          { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              bottom: `${rise}%`,
              left: positions[i],
              width: 80,
              height: 300,
              borderRadius: 40,
              backgroundColor: COLORS.green,
              opacity: 0.12,
            }}
          />
        );
      })}
      <div style={{ position: "relative", zIndex: 1, textAlign: "center" }}>
        <div
          style={{
            fontFamily: FONTS.sans,
            fontSize: 52,
            fontWeight: 700,
            color: COLORS.text,
            opacity: urlProgress,
            transform: `translateY(${(1 - urlProgress) * 30}px)`,
          }}
        >
          ttslibrary.com
        </div>
        <div
          style={{
            width: `${underlineWidth}%`,
            height: 4,
            backgroundColor: COLORS.green,
            margin: "12px auto 0",
            borderRadius: 2,
          }}
        />
        <div
          style={{
            fontFamily: FONTS.sans,
            fontSize: 18,
            color: COLORS.textMuted,
            marginTop: 16,
            opacity: interpolate(frame, [30, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          Built by Telnyx
        </div>
      </div>
    </div>
  );
};

// Main Composition
export const TTSLibraryPromo: React.FC = () => {
  return (
    <Series>
      <Series.Sequence durationInFrames={90}><HookScene /></Series.Sequence>
      <Series.Sequence durationInFrames={120}><StatsScene /></Series.Sequence>
      <Series.Sequence durationInFrames={90}><ProvidersScene /></Series.Sequence>
      <Series.Sequence durationInFrames={120}><UIPreviewScene /></Series.Sequence>
      <Series.Sequence durationInFrames={90}><ValuePropScene /></Series.Sequence>
      <Series.Sequence durationInFrames={90}><CTAScene /></Series.Sequence>
    </Series>
  );
};