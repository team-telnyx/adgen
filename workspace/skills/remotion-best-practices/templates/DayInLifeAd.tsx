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
import { ChatBubble } from "../components/ChatBubble";

export interface DayScene {
  /** Time label (e.g., "7:14 AM") */
  time: string;
  /** Scene label (e.g., "Morning commute") */
  label: string;
  /** Emoji icon for the scene */
  emoji?: string;
  /** User's voice message */
  userMessage: string;
  /** Bot's reply */
  botReply: string;
  /** Voice message duration (e.g., "0:03") */
  voiceDuration?: string;
}

export interface DayInLifeAdProps {
  /** Array of scenes in chronological order */
  scenes: DayScene[];
  /** Product/brand name */
  brandName?: string;
  /** Tagline for end card */
  tagline?: string;
  /** CTA URL */
  ctaUrl?: string;
  /** Duration per scene in frames */
  sceneDuration?: number;
  /** Duration of time card in frames */
  timeCardDuration?: number;
  /** End card duration in frames */
  endCardDuration?: number;
}

const TimeCard: React.FC<{ time: string; label: string; emoji?: string }> = ({
  time,
  label,
  emoji,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const timeSpring = spring({
    frame: frame - 5,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  const labelSpring = spring({
    frame: frame - 20,
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
        flexDirection: "column",
        gap: 12,
      }}
    >
      {emoji && (
        <div
          style={{
            fontSize: 48,
            opacity: timeSpring,
            transform: `scale(${interpolate(timeSpring, [0, 1], [0.5, 1])})`,
          }}
        >
          {emoji}
        </div>
      )}
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 72,
          fontWeight: 200,
          color: COLORS.text,
          letterSpacing: -1,
          opacity: timeSpring,
          transform: `translateY(${interpolate(timeSpring, [0, 1], [20, 0])}px)`,
        }}
      >
        {time}
      </div>
      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 20,
          fontWeight: 400,
          color: COLORS.textMuted,
          opacity: labelSpring,
          transform: `translateY(${interpolate(labelSpring, [0, 1], [15, 0])}px)`,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};

const ChatScene: React.FC<{
  userMessage: string;
  botReply: string;
  voiceDuration?: string;
}> = ({ userMessage, botReply, voiceDuration = "0:03" }) => {
  const frame = useCurrentFrame();

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
          width: "100%",
          maxWidth: 600,
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        {/* User voice message */}
        <ChatBubble
          message={`🎤 ${voiceDuration}`}
          isUser
          delay={10}
          userColor="#2B5278"
        />
        
        {/* Transcription */}
        <div
          style={{
            fontFamily: FONTS.sans,
            fontSize: 14,
            color: COLORS.textMuted,
            fontStyle: "italic",
            marginLeft: 20,
            opacity: interpolate(frame, [20, 35], [0, 1], { extrapolateRight: "clamp" }),
          }}
        >
          "{userMessage}"
        </div>

        {/* Bot reply */}
        <ChatBubble
          message={botReply}
          isUser={false}
          delay={60}
          showTyping
          typingDuration={25}
        />
      </div>
    </AbsoluteFill>
  );
};

const EndCard: React.FC<{
  brandName: string;
  tagline: string;
  ctaUrl: string;
}> = ({ brandName, tagline, ctaUrl }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const tagSpring = spring({
    frame: frame - 10,
    fps,
    config: SPRING_CONFIG.bouncy,
  });

  const urlSpring = spring({
    frame: frame - 40,
    fps,
    config: SPRING_CONFIG.smooth,
  });

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
          fontFamily: FONTS.sans,
          fontSize: 48,
          fontWeight: 700,
          color: COLORS.text,
          textAlign: "center",
          lineHeight: 1.3,
          opacity: tagSpring,
          transform: `translateY(${interpolate(tagSpring, [0, 1], [30, 0])}px)`,
          padding: "0 60px",
        }}
      >
        {tagline.split("{green}").map((part, i) =>
          i === 0 ? (
            part
          ) : (
            <React.Fragment key={i}>
              <span style={{ color: COLORS.telnyxGreen }}>{part}</span>
            </React.Fragment>
          )
        )}
      </div>

      <div
        style={{
          fontFamily: FONTS.sans,
          fontSize: 24,
          fontWeight: 700,
          color: COLORS.telnyxGreen,
          opacity: urlSpring,
          transform: `translateY(${interpolate(urlSpring, [0, 1], [15, 0])}px)`,
          letterSpacing: 2,
        }}
      >
        {ctaUrl}
      </div>
    </AbsoluteFill>
  );
};

export const DayInLifeAd: React.FC<DayInLifeAdProps> = ({
  scenes,
  brandName = "ClawdTalk",
  tagline = "Give your thumbs a break.{green}",
  ctaUrl = "clawdtalk.com",
  sceneDuration = 180,
  timeCardDuration = 60,
  endCardDuration = 180,
}) => {
  let offset = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {scenes.map((scene, i) => {
        const timeStart = offset;
        offset += timeCardDuration;

        const chatStart = offset;
        offset += sceneDuration;

        return (
          <React.Fragment key={i}>
            <Sequence from={timeStart} durationInFrames={timeCardDuration}>
              <TimeCard
                time={scene.time}
                label={scene.label}
                emoji={scene.emoji}
              />
            </Sequence>
            <Sequence from={chatStart} durationInFrames={sceneDuration}>
              <ChatScene
                userMessage={scene.userMessage}
                botReply={scene.botReply}
                voiceDuration={scene.voiceDuration}
              />
            </Sequence>
          </React.Fragment>
        );
      })}

      <Sequence from={offset} durationInFrames={endCardDuration}>
        <EndCard brandName={brandName} tagline={tagline} ctaUrl={ctaUrl} />
      </Sequence>
    </AbsoluteFill>
  );
};
