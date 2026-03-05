import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { COLORS, SPRING_CONFIG } from "../theme";

export interface ChatBubbleProps {
  /** Message text content */
  message: string;
  /** Whether this is sent by user (right-aligned) or bot (left-aligned) */
  isUser?: boolean;
  /** Timestamp shown below message */
  timestamp?: string;
  /** Animation delay in frames */
  delay?: number;
  /** Custom bubble color for user messages */
  userColor?: string;
  /** Custom bubble color for bot messages */
  botColor?: string;
  /** Show typing indicator before message appears */
  showTyping?: boolean;
  /** Duration of typing animation in frames */
  typingDuration?: number;
}

const TypingIndicator: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <div style={{ display: "flex", gap: 4, padding: "8px 4px" }}>
      {[0, 1, 2].map((i) => {
        const bounce = Math.sin(frame * 0.2 + i * 0.8) * 4;
        return (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: 4,
              backgroundColor: "#666",
              transform: `translateY(${-Math.abs(bounce)}px)`,
            }}
          />
        );
      })}
    </div>
  );
};

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  message,
  isUser = false,
  timestamp,
  delay = 0,
  userColor = COLORS.telnyxGreenDim,
  botColor = "#1a1a1a",
  showTyping = false,
  typingDuration = 20,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const localFrame = frame - delay;
  const isTyping = showTyping && localFrame < typingDuration;
  const messageStart = showTyping ? typingDuration : 0;

  const slideProgress = spring({
    frame: localFrame - messageStart,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  const opacity = interpolate(slideProgress, [0, 1], [0, 1]);

  const bubbleColor = isUser ? userColor : botColor;
  const alignStyle = isUser ? { alignSelf: "flex-end" } : { alignSelf: "flex-start" };
  const borderRadius = isUser
    ? "16px 16px 4px 16px"
    : "16px 16px 16px 4px";

  if (localFrame < 0) return null;

  return (
    <div
      style={{
        ...alignStyle,
        maxWidth: "80%",
        opacity: localFrame >= messageStart ? opacity : 1,
        transform: `translateY(${interpolate(slideProgress, [0, 1], [20, 0])}px)`,
      }}
    >
      {isTyping ? (
        <div
          style={{
            backgroundColor: botColor,
            borderRadius: "16px",
            padding: "8px 16px",
            border: `1px solid #333`,
          }}
        >
          <TypingIndicator />
        </div>
      ) : (
        <>
          <div
            style={{
              backgroundColor: bubbleColor,
              borderRadius,
              padding: "12px 16px",
              border: isUser ? `1px solid ${COLORS.telnyxGreen}33` : `1px solid #333`,
            }}
          >
            <div
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: 16,
                color: COLORS.text,
                lineHeight: 1.4,
                whiteSpace: "pre-wrap",
              }}
            >
              {message}
            </div>
          </div>
          {timestamp && (
            <div
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: 11,
                color: COLORS.textMuted,
                textAlign: isUser ? "right" : "left",
                marginTop: 4,
              }}
            >
              {timestamp}
            </div>
          )}
        </>
      )}
    </div>
  );
};
