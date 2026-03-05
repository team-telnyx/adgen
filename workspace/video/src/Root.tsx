import React from "react";
import { Composition } from "remotion";
import { ProductLaunch } from "./compositions/ProductLaunch";
import { SocialAd } from "./compositions/SocialAd";
import { StatReveal } from "./compositions/StatReveal";
import { FeatureDemo } from "./compositions/FeatureDemo";
import { ClipAssembly } from "./compositions/ClipAssembly";
import { FORMAT_DIMENSIONS } from "./theme";

const FPS = 30;

const defaultProps = {
  headline: "Your Headline Here",
  subhead: "Supporting copy goes here",
  cta: "Learn More",
  heroImage: "",
  accentColor: "#00C26E",
  format: "landscape" as const,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ProductLaunch — 15s */}
      <Composition
        id="ProductLaunch"
        component={ProductLaunch}
        durationInFrames={15 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.landscape.width}
        height={FORMAT_DIMENSIONS.landscape.height}
        defaultProps={defaultProps}
      />
      <Composition
        id="ProductLaunch-square"
        component={ProductLaunch}
        durationInFrames={15 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.square.width}
        height={FORMAT_DIMENSIONS.square.height}
        defaultProps={{ ...defaultProps, format: "square" }}
      />
      <Composition
        id="ProductLaunch-vertical"
        component={ProductLaunch}
        durationInFrames={15 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.vertical.width}
        height={FORMAT_DIMENSIONS.vertical.height}
        defaultProps={{ ...defaultProps, format: "vertical" }}
      />

      {/* SocialAd — 7s */}
      <Composition
        id="SocialAd"
        component={SocialAd}
        durationInFrames={7 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.landscape.width}
        height={FORMAT_DIMENSIONS.landscape.height}
        defaultProps={defaultProps}
      />
      <Composition
        id="SocialAd-square"
        component={SocialAd}
        durationInFrames={7 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.square.width}
        height={FORMAT_DIMENSIONS.square.height}
        defaultProps={{ ...defaultProps, format: "square" }}
      />
      <Composition
        id="SocialAd-vertical"
        component={SocialAd}
        durationInFrames={7 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.vertical.width}
        height={FORMAT_DIMENSIONS.vertical.height}
        defaultProps={{ ...defaultProps, format: "vertical" }}
      />

      {/* StatReveal — 10s */}
      <Composition
        id="StatReveal"
        component={StatReveal}
        durationInFrames={10 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.landscape.width}
        height={FORMAT_DIMENSIONS.landscape.height}
        defaultProps={{ ...defaultProps, headline: "40%" }}
      />
      <Composition
        id="StatReveal-square"
        component={StatReveal}
        durationInFrames={10 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.square.width}
        height={FORMAT_DIMENSIONS.square.height}
        defaultProps={{ ...defaultProps, headline: "40%", format: "square" }}
      />
      <Composition
        id="StatReveal-vertical"
        component={StatReveal}
        durationInFrames={10 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.vertical.width}
        height={FORMAT_DIMENSIONS.vertical.height}
        defaultProps={{ ...defaultProps, headline: "40%", format: "vertical" }}
      />

      {/* FeatureDemo — 18s */}
      <Composition
        id="FeatureDemo"
        component={FeatureDemo}
        durationInFrames={18 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.landscape.width}
        height={FORMAT_DIMENSIONS.landscape.height}
        defaultProps={defaultProps}
      />
      <Composition
        id="FeatureDemo-square"
        component={FeatureDemo}
        durationInFrames={18 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.square.width}
        height={FORMAT_DIMENSIONS.square.height}
        defaultProps={{ ...defaultProps, format: "square" }}
      />
      <Composition
        id="FeatureDemo-vertical"
        component={FeatureDemo}
        durationInFrames={18 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.vertical.width}
        height={FORMAT_DIMENSIONS.vertical.height}
        defaultProps={{ ...defaultProps, format: "vertical" }}
      />
      {/* ClipAssembly — variable duration */}
      <Composition
        id="ClipAssembly"
        component={ClipAssembly}
        durationInFrames={60 * FPS}
        fps={FPS}
        width={FORMAT_DIMENSIONS.landscape.width}
        height={FORMAT_DIMENSIONS.landscape.height}
        defaultProps={{
          clips: [],
          musicSrc: undefined,
          logoSrc: undefined,
          titleCard: undefined,
        }}
      />
    </>
  );
};
