import { AbsoluteFill, Sequence, Video, Audio, Img, useVideoConfig } from "remotion";
import { staticFile } from "remotion";

export interface ClipAssemblyProps {
  clips: Array<{
    src: string;
    startFrom?: number;
    endAt?: number;
    durationInFrames?: number;
  }>;
  musicSrc?: string;
  logoSrc?: string;
  titleCard?: {
    text: string;
    durationInFrames: number;
  };
}

export const ClipAssembly: React.FC<ClipAssemblyProps> = ({
  clips,
  musicSrc,
  logoSrc,
  titleCard,
}) => {
  const { fps } = useVideoConfig();
  let currentFrame = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {titleCard && (
        <Sequence from={0} durationInFrames={titleCard.durationInFrames}>
          <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
            <h1 style={{ color: "#F5F0E8", fontFamily: "PP Formula", fontSize: 72 }}>
              {titleCard.text}
            </h1>
          </AbsoluteFill>
        </Sequence>
      )}

      {clips.map((clip, i) => {
        const from = currentFrame + (titleCard?.durationInFrames ?? 0);
        const dur = clip.durationInFrames ?? Math.round((clip.endAt ?? 10) - (clip.startFrom ?? 0)) * fps;
        const el = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <Video
              src={clip.src}
              startFrom={Math.round((clip.startFrom ?? 0) * fps)}
              endAt={clip.endAt ? Math.round(clip.endAt * fps) : undefined}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </Sequence>
        );
        currentFrame += dur;
        return el;
      })}

      {musicSrc && <Audio src={musicSrc} volume={0.3} />}

      {logoSrc && (
        <Img
          src={logoSrc}
          style={{
            position: "absolute",
            top: 20,
            right: 20,
            width: 120,
            opacity: 0.8,
          }}
        />
      )}
    </AbsoluteFill>
  );
};
