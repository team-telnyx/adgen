import { useCurrentFrame } from "remotion";

export interface TextCutProps {
  texts: string[];
  frameDuration: number;
  fontSize?: number;
  fontFamily?: string;
  color?: string;
}

export const TextCut: React.FC<TextCutProps> = ({
  texts,
  frameDuration,
  fontSize = 120,
  fontFamily = '"Georgia", "Times New Roman", serif',
  color = "#000000",
}) => {
  const frame = useCurrentFrame();
  const index = Math.floor(frame / frameDuration) % texts.length;

  return (
    <span
      style={{
        fontFamily,
        fontSize,
        color,
        fontWeight: 400,
      }}
    >
      {texts[index]}
    </span>
  );
};
