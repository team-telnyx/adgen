import React from "react";
import { AbsoluteFill, Series, useVideoConfig } from "remotion";
import { AnimatedText } from "../components/AnimatedText";
import { SceneWrapper } from "../components/SceneWrapper";
import { CodeBlock } from "../components/CodeBlock";
import { COLORS } from "../theme";

export interface ProductLaunchProps {
  productName: string;
  tagline: string;
  features: { icon: string; title: string; desc: string }[];
  codeExample: string;
  ctaText: string;
  ctaUrl: string;
}

const S = { h: 90, p: 180, i: 180, f: 240, c: 240, cta: 150 }; // frame counts
const T = S.h + S.p + S.i + S.f + S.c + S.cta;

// Scene 1: HOOK
const Hook = ({ t }: { t: string }) => (
  <SceneWrapper from={0} durationInFrames={S.h}>
    <AbsoluteFill style={{ backgroundColor: COLORS.background, justifyContent: "center", alignItems: "center" }}>
      <AnimatedText text={t} variant="slideUp" fontSize={60} fontWeight={800} style={{ textAlign: "center", maxWidth: "85%", lineHeight: 1.3 }}>
        {t.split(/(\{[^\}]+\})/).map((p, i) => p.match(/\{([^}]+)\}/) ? <span key={i} style={{ color: COLORS.telnyxGreen }}>{p.slice(1, -1)}</span> : p)}
      </AnimatedText>
    </AbsoluteFill>
  </SceneWrapper>
);

// Scene 2: PROBLEM
const Problem = () => (
  <SceneWrapper from={S.h} durationInFrames={S.p}>
    <AbsoluteFill style={{ backgroundColor: COLORS.background, justifyContent: "center", alignItems: "center" }}>
      <AnimatedText text="The old way?" variant="fadeIn" fontSize={32} color={COLORS.textMuted} />
      <div style={{ display: "flex", gap: 16, marginTop: 40 }}>
        {["Manual", "Slow", "Error-prone"].map((w, i) => (
          <div key={i} style={{ backgroundColor: COLORS.backgroundLight, padding: "14px 28px", borderRadius: 10, border: "1px solid #333" }}>
            <AnimatedText text={w} variant="slideUp" delay={20 + i * 15} fontSize={22} fontWeight={600} />
          </div>
        ))}
      </div>
    </AbsoluteFill>
  </SceneWrapper>
);

// Scene 3: INTRO
const Intro = ({ n }: { n: string }) => (
  <SceneWrapper from={S.h + S.p} durationInFrames={S.i}>
    <AbsoluteFill style={{ backgroundColor: COLORS.background, justifyContent: "center", alignItems: "center" }}>
      <AnimatedText text="Introducing" variant="fadeIn" fontSize={26} color={COLORS.textMuted} delay={15} />
      <AnimatedText text={n} variant="slideUp" fontSize={64} fontWeight={800} color={COLORS.telnyxGreen} delay={30} style={{ marginTop: 12 }} />
    </AbsoluteFill>
  </SceneWrapper>
);

// Scene 4: FEATURES
const Features = ({ fts }: { fts: ProductLaunchProps["features"] }) => (
  <SceneWrapper from={S.h + S.p + S.i} durationInFrames={S.f}>
    <AbsoluteFill style={{ backgroundColor: COLORS.background, padding: 50, justifyContent: "center" }}>
      <AnimatedText text="What you get" variant="fadeIn" fontSize={36} fontWeight={700} style={{ marginBottom: 40, textAlign: "center" }} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, maxWidth: 850, margin: "0 auto" }}>
        {fts.map((f, i) => (
          <div key={i} style={{ backgroundColor: COLORS.backgroundLight, borderRadius: 14, padding: 24, border: "1px solid #333" }}>
            <AnimatedText text={f.icon} delay={10 + i * 12} fontSize={28} />
            <AnimatedText text={f.title} variant="slideUp" delay={15 + i * 12} fontSize={20} fontWeight={700} style={{ marginTop: 10 }} />
            <AnimatedText text={f.desc} variant="fadeIn" delay={25 + i * 12} fontSize={15} color={COLORS.textMuted} style={{ marginTop: 6 }} />
          </div>
        ))}
      </div>
    </AbsoluteFill>
  </SceneWrapper>
);

// Scene 5: CODE
const CodeDemo = ({ code }: { code: string }) => (
  <SceneWrapper from={S.h + S.p + S.i + S.f} durationInFrames={S.c}>
    <AbsoluteFill style={{ backgroundColor: COLORS.background, justifyContent: "center", alignItems: "center", padding: 30 }}>
      <AnimatedText text="Simple to use" variant="fadeIn" fontSize={28} color={COLORS.textMuted} style={{ marginBottom: 24 }} />
      <div style={{ width: "100%", maxWidth: 650 }}><CodeBlock code={code} language="json" fontSize={14} /></div>
    </AbsoluteFill>
  </SceneWrapper>
);

// Scene 6: CTA
const CTA = ({ txt, url }: { txt: string; url: string }) => (
  <SceneWrapper from={S.h + S.p + S.i + S.f + S.c} durationInFrames={S.cta}>
    <AbsoluteFill style={{ backgroundColor: COLORS.background, justifyContent: "center", alignItems: "center" }}>
      <AnimatedText text="Ready to start?" variant="fadeIn" fontSize={26} color={COLORS.textMuted} />
      <AnimatedText text={txt} variant="slideUp" fontSize={44} fontWeight={700} color={COLORS.telnyxGreen} delay={20} style={{ marginTop: 16 }} />
    </AbsoluteFill>
  </SceneWrapper>
);

// Main Composition
export const ProductLaunch: React.FC<ProductLaunchProps> = ({ productName, tagline, features, codeExample, ctaText, ctaUrl }) => (
  <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
    <Series>
      <Series.Sequence durationInFrames={S.h}><Hook tagline={tagline} /></Series.Sequence>
      <Series.Sequence durationInFrames={S.p}><Problem /></Series.Sequence>
      <Series.Sequence durationInFrames={S.i}><Intro productName={productName} /></Series.Sequence>
      <Series.Sequence durationInFrames={S.f}><Features fts={features} /></Series.Sequence>
      <Series.Sequence durationInFrames={S.c}><CodeDemo code={codeExample} /></Series.Sequence>
      <Series.Sequence durationInFrames={S.cta}><CTA txt={ctaText} url={ctaUrl} /></Series.Sequence>
    </Series>
  </AbsoluteFill>
);

export default ProductLaunch;
