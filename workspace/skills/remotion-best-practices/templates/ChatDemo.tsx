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
import { ChatBubble, type ChatBubbleProps } from "../components/ChatBubble";

export interface ChatMessage extends Omit<ChatBubbleProps, "delay"> {
  /** Delay before this message appears (frames) */
  delay: number;
}

export interface ChatDemoProps {
  /** Array of chat messages to display */
  messages: ChatMessage[];
  /** Chat header title */
  headerTitle?: string;
  /** Chat header subtitle (e.g., "online") */
  headerSubtitle?: string;
  /** Typing speed multiplier (1 = normal, 0.5 = faster) */
  typingSpeed?: number;
  /** Custom user bubble color */
  userBubbleColor?: string;
  /** Custom bot bubble color */
  botBubbleColor?: string;
  /** Background color */
  backgroundColor?: string;
}

const ChatHeader: React.FC<{
  title: string;
  subtitle: string;
  avatarEmoji?: string;
}> = ({ title, subtitle, avatarEmoji = "🤖" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    config: SPRING_CONFIG.smooth,
  });

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        paddingBottom: 16,
        borderBottom: "1px solid #333",
        opacity: progress,
        transform: `translateY(${interpolate(progress, [0, 1], [-20, 0])}px)`,
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 22,
          background: `linear-gradient(135deg, ${COLORS.telnyxGreen}, #00B88A)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 22,
        }}
      >
        {avatarEmoji}
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
          {title}
        </div>
        <div
          style={{
            fontFamily: FONTS.sans,
            fontSize: 13,
            color: COLORS.telnyxGreen,
          }}
        >
          {subtitle}
        </div>
      </div>
    </div>
  );
};

export const ChatDemo: React.FC<ChatDemoProps> = ({
  messages,
  headerTitle = "AI Assistant",
  headerSubtitle = "online",
  typingSpeed = 1,
  userBubbleColor,
  botBubbleColor,
  backgroundColor = "#0A0A0A",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate total duration from last message
  const lastMessage = messages[messages.length - 1];
  const totalDuration = lastMessage ? lastMessage.delay + 90 : 180;

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 40,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 600,
          height: "80%",
          backgroundColor: "#111",
          borderRadius: 24,
          padding: 20,
          display: "flex",
          flexDirection: "column",
          border: "1px solid #222",
          boxShadow: `0 0 60px ${COLORS.telnyxGreen}11`,
        }}
      >
        <ChatHeader title={headerTitle} subtitle={headerSubtitle} />

        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 14,
            padding: "20px 0",
            overflow: "hidden",
          }}
        >
          {messages.map((msg, i) => (
            <ChatBubble
              key={i}
              message={msg.message}
              isUser={msg.isUser}
              timestamp={msg.timestamp}
              delay={msg.delay}
              showTyping={msg.showTyping && i > 0 && !msg.isUser}
              typingDuration={Math.round(20 / typingSpeed)}
              userColor={userBubbleColor}
              botColor={botBubbleColor}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
