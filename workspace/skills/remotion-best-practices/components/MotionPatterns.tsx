/**
 * TerminalMotion.tsx
 *
 * Reusable terminal/CLI motion components for Remotion.
 * Extracted from the Telnyx CLI promo video project.
 *
 * Patterns included:
 * - TerminalZoom: ScreenStudio-style camera zoom/pan choreography
 * - TerminalPan: Smooth panning across terminal content
 * - AsciiReveal: Character-by-character ASCII art animation
 * - TypewriterText: Typing animation with blinking cursor
 * - GlitchText: RGB split glitch effect
 * - CLITableReveal: Row-by-row table reveal with stagger
 * - TerminalWindow: Spring-based slide-in terminal window
 */

import React, { useMemo } from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";

// ============================================================================
// TYPES
// ============================================================================

export interface TerminalZoomPhase {
  /** Start frame for this phase */
  startFrame: number;
  /** End frame for this phase */
  endFrame: number;
  /** Target scale at end of phase (1.0 = 100%) */
  targetScale: number;
  /** Horizontal translation in pixels (positive = right) */
  translateX: number;
  /** Vertical translation in pixels (positive = down) */
  translateY: number;
  /** Easing function for smooth motion */
  easing?: (t: number) => number;
}

export interface TerminalZoomProps {
  /** Array of camera phases for choreography */
  phases: TerminalZoomPhase[];
  /** Content to be zoomed/panned */
  children: React.ReactNode;
  /** Additional styles for the container */
  style?: React.CSSProperties;
  /** Extend background to prevent clipping during zoom (default: 1000) */
  backgroundExtension?: number;
}

export interface TerminalPanProps {
  /** Starting X position */
  startX: number;
  /** Ending X position */
  endX: number;
  /** Starting Y position */
  startY: number;
  /** Ending Y position */
  endY: number;
  /** Animation duration in frames */
  durationInFrames: number;
  /** Delay before animation starts */
  delay?: number;
  /** Easing function (default: Easing.inOut(Easing.cubic)) */
  easing?: (t: number) => number;
  /** Content to pan */
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export interface AsciiRevealProps {
  /** The ASCII art string to reveal */
  text: string;
  /** Start frame for the reveal */
  startFrame: number;
  /** Frames between each character reveal */
  charDelay?: number;
  /** Color of the ASCII text */
  color?: string;
  /** Font family (default: monospace) */
  fontFamily?: string;
  /** Font size in pixels */
  fontSize?: number;
  /** Line height */
  lineHeight?: number;
  /** Show cursor at end (default: true) */
  showCursor?: boolean;
  /** Cursor blink speed in frames (default: 20) */
  cursorSpeed?: number;
  style?: React.CSSProperties;
}

export interface TypewriterTextProps {
  /** Text to type out */
  text: string;
  /** Frame to start typing */
  startFrame: number;
  /** Characters per second (higher = faster, default: 25) */
  speed?: number;
  /** Additional CSS classes */
  className?: string;
  /** Show blinking cursor (default: true) */
  showCursor?: boolean;
  /** Cursor color (default: #00E3AA) */
  cursorColor?: string;
  style?: React.CSSProperties;
}

export interface GlitchTextProps {
  /** Text to display with glitch effect */
  text: string;
  /** Frame to start glitch */
  startFrame?: number;
  /** Duration of glitch in frames (default: 60) */
  duration?: number;
  /** Start immediately without fade-in (default: false) */
  immediate?: boolean;
  /** Additional CSS classes */
  className?: string;
  style?: React.CSSProperties;
}

export interface CLITableRevealProps {
  /** Table header columns */
  headers: { key: string; width: number }[];
  /** Table data rows */
  rows: Record<string, string>[];
  /** Frame to start reveal */
  startFrame: number;
  /** Frames between each row (default: 6) */
  rowDelay?: number;
  /** Spring config for row animation */
  springConfig?: {
    damping: number;
    stiffness: number;
    mass: number;
  };
  /** Primary color for accents */
  accentColor?: string;
  style?: React.CSSProperties;
}

export interface TerminalWindowProps {
  /** Content inside terminal */
  children: React.ReactNode;
  /** Frame to start animation */
  startFrame?: number;
  /** Spring configuration */
  springConfig?: {
    damping: number;
    stiffness: number;
    mass: number;
  };
  /** Window title (default: "terminal — zsh") */
  title?: string;
  /** Additional CSS classes */
  className?: string;
  style?: React.CSSProperties;
}

// ============================================================================
// TERMINAL ZOOM - ScreenStudio-style camera choreography
// ============================================================================

/**
 * Multi-phase camera zoom and pan for terminal content.
 * Simulates ScreenStudio-style camera movements.
 *
 * @example
 * ```tsx
 * <TerminalZoom
 *   phases={[
 *     { startFrame: 50, endFrame: 100, targetScale: 1.8, translateX: 200, translateY: 100 },
 *     { startFrame: 100, endFrame: 150, targetScale: 1.4, translateX: 200, translateY: -50 },
 *   ]}
 * >
 *   <TerminalContent />
 * </TerminalZoom>
 * ```
 */
export const TerminalZoom: React.FC<TerminalZoomProps> = ({
  phases,
  children,
  style,
  backgroundExtension = 1000,
}) => {
  const frame = useCurrentFrame();

  // Calculate cumulative scale and translation
  let scale = 1.0;
  let x = 0;
  let y = 0;

  for (let i = 0; i < phases.length; i++) {
    const phase = phases[i];
    const progress = interpolate(
      frame,
      [phase.startFrame, phase.endFrame],
      [0, 1],
      {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: phase.easing ?? Easing.bezier(0.65, 0, 0.35, 1),
      }
    );

    const prevScale = i === 0 ? 1.0 : scale;
    scale = interpolate(progress, [0, 1], [prevScale, phase.targetScale]);

    const prevX = i === 0 ? 0 : x;
    const prevY = i === 0 ? 0 : y;
    x = interpolate(progress, [0, 1], [prevX, phase.translateX]);
    y = interpolate(progress, [0, 1], [prevY, phase.translateY]);
  }

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        transform: `scale(${scale}) translate(${x}px, ${y}px)`,
        transformOrigin: "center center",
        willChange: "transform",
        ...style,
      }}
    >
      {/* Extended background to prevent clipping during zoom */}
      <div
        style={{
          position: "absolute",
          inset: -backgroundExtension,
          pointerEvents: "none",
        }}
      />
      {children}
    </div>
  );
};

// ============================================================================
// TERMINAL PAN - Smooth panning across content
// ============================================================================

/**
 * Smooth panning animation across terminal content.
 * Useful for highlighting specific areas of a terminal.
 *
 * @example
 * ```tsx
 * <TerminalPan
 *   startX={0}
 *   endX={-200}
 *   startY={0}
 *   endY={100}
 *   durationInFrames={60}
 *   delay={30}
 * >
 *   <TerminalContent />
 * </TerminalPan>
 * ```
 */
export const TerminalPan: React.FC<TerminalPanProps> = ({
  startX,
  endX,
  startY,
  endY,
  durationInFrames,
  delay = 0,
  easing = Easing.inOut(Easing.cubic),
  children,
  style,
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = Math.max(0, frame - delay);

  const x = interpolate(
    adjustedFrame,
    [0, durationInFrames],
    [startX, endX],
    { extrapolateRight: "clamp", easing }
  );

  const y = interpolate(
    adjustedFrame,
    [0, durationInFrames],
    [startY, endY],
    { extrapolateRight: "clamp", easing }
  );

  return (
    <div
      style={{
        transform: `translate(${x}px, ${y}px)`,
        willChange: "transform",
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// ============================================================================
// ASCII REVEAL - Character-by-character animation
// ============================================================================

/**
 * Reveals ASCII art character by character like a dot matrix display.
 * Perfect for logo reveals and retro terminal effects.
 *
 * @example
 * ```tsx
 * <AsciiReveal
 *   text="HELLO"
 *   startFrame={0}
 *   charDelay={2}
 *   color="#00E3AA"
 *   fontSize={20}
 * />
 * ```
 */
export const AsciiReveal: React.FC<AsciiRevealProps> = ({
  text,
  startFrame,
  charDelay = 2,
  color = "#00E3AA",
  fontFamily = "JetBrains Mono, monospace",
  fontSize = 16,
  lineHeight = 1.2,
  showCursor = true,
  cursorSpeed = 20,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lines = text.split("\n");
  const totalChars = lines.reduce((acc, line) => acc + line.length, 0);

  // Calculate which characters should be visible
  const visibleChars = Math.floor((frame - startFrame) / charDelay);

  let charCount = 0;
  const renderedLines = lines.map((line, lineIndex) => {
    const lineChars = line.split("").map((char, charIndex) => {
      charCount++;
      const isVisible = charCount <= visibleChars;

      // Spring animation for each character
      const charProgress = spring({
        frame: frame - (startFrame + charCount * charDelay),
        fps,
        config: {
          damping: 15,
          stiffness: 200,
          mass: 0.5,
        },
      });

      const scale = interpolate(charProgress, [0, 1], [0, 1]);
      const opacity = isVisible ? interpolate(scale, [0, 0.5, 1], [0, 0.7, 1]) : 0;

      return (
        <span
          key={`${lineIndex}-${charIndex}`}
          style={{
            display: "inline-block",
            transform: `scale(${scale})`,
            opacity,
            color,
            fontFamily,
            fontSize,
            lineHeight,
          }}
        >
          {char}
        </span>
      );
    });

    return (
      <div key={lineIndex} style={{ whiteSpace: "pre" }}>
        {lineChars}
        {lineIndex === lines.length - 1 && showCursor && (
          <Cursor
            visible={visibleChars >= totalChars}
            speed={cursorSpeed}
            color={color}
          />
        )}
      </div>
    );
  });

  if (frame < startFrame) return null;

  return <div style={style}>{renderedLines}</div>;
};

// Cursor helper component
const Cursor: React.FC<{ visible: boolean; speed: number; color: string }> = ({
  visible,
  speed,
  color,
}) => {
  const frame = useCurrentFrame();
  const isVisible = visible && frame % speed < speed * 0.75;

  return (
    <span
      style={{
        display: "inline-block",
        width: "0.6em",
        height: "1em",
        backgroundColor: color,
        marginLeft: "0.1em",
        verticalAlign: "middle",
        opacity: isVisible ? 1 : 0,
        boxShadow: `0 0 8px ${color}`,
      }}
    />
  );
};

// ============================================================================
// TYPEWRITER TEXT - Typing animation with cursor
// ============================================================================

/**
 * Simulates typing text with a blinking cursor.
 * Configurable speed for realistic terminal feel.
 *
 * @example
 * ```tsx
 * <TypewriterText
 *   text="telnyx number search --country US"
 *   startFrame={45}
 *   speed={30}
 *   cursorColor="#00E3AA"
 * />
 * ```
 */
export const TypewriterText: React.FC<TypewriterTextProps> = ({
  text,
  startFrame,
  speed = 25,
  className = "",
  showCursor = true,
  cursorColor = "#00E3AA",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const charsPerFrame = speed / fps;
  const elapsedFrames = Math.max(0, frame - startFrame);
  const visibleChars = Math.floor(elapsedFrames * charsPerFrame);
  const displayText = text.slice(0, visibleChars);

  // Cursor blink: solid during typing, blinking after complete
  const isComplete = visibleChars >= text.length;
  const cursorVisible =
    showCursor &&
    (!isComplete || frame % 20 < 15);

  return (
    <span className={`${className} whitespace-pre`} style={style}>
      {displayText}
      {cursorVisible && (
        <span
          style={{
            display: "inline-block",
            width: "0.5em",
            height: "1em",
            backgroundColor: cursorColor,
            marginLeft: "0.05em",
            verticalAlign: "middle",
            boxShadow: `0 0 8px ${cursorColor}99`,
          }}
        />
      )}
    </span>
  );
};

// ============================================================================
// GLITCH TEXT - RGB split effect
// ============================================================================

/**
 * Applies a cyberpunk-style RGB split glitch effect to text.
 * Great for transitions and emphasizing commands.
 *
 * @example
 * ```tsx
 * <GlitchText
 *   text="SYSTEM ERROR"
 *   startFrame={100}
 *   duration={60}
 *   immediate={false}
 * />
 * ```
 */
export const GlitchText: React.FC<GlitchTextProps> = ({
  text,
  startFrame = 0,
  duration = 60,
  immediate = false,
  className = "",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const endFrame = startFrame + duration;

  // Main text opacity
  const opacity = immediate
    ? interpolate(
        frame,
        [startFrame, endFrame - 15, endFrame],
        [1, 1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      )
    : interpolate(
        frame,
        [startFrame, startFrame + 10, endFrame - 10, endFrame],
        [0, 1, 1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

  // Glitch intensity with spring
  const glitchSpring = spring({
    frame: frame - startFrame,
    fps,
    config: {
      damping: immediate ? 8 : 10,
      stiffness: immediate ? 150 : 100,
      mass: 0.4,
    },
  });

  const glitchIntensity = immediate
    ? interpolate(
        frame,
        [startFrame, startFrame + 15, endFrame - 15, endFrame],
        [0.8, 0.2, 0.2, 0.8],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      )
    : interpolate(
        frame,
        [startFrame, startFrame + 20, endFrame - 20, endFrame],
        [1, 0.3, 0.3, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

  // Generate glitch offsets
  const glitchOffset1 = Math.sin(frame * 0.5) * 3 * glitchIntensity;
  const glitchOffset2 = Math.cos(frame * 0.7) * 2 * glitchIntensity;
  const sliceOffset = Math.sin(frame * 0.3) * 5 * glitchIntensity;

  // RGB split effect
  const rgbOffset =
    interpolate(
      frame,
      [startFrame, startFrame + 5, startFrame + 10],
      [10, 3, 0],
      { extrapolateLeft: "clamp" }
    ) * glitchIntensity;

  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  return (
    <div
      className={`relative font-mono font-bold ${className}`}
      style={{ opacity, ...style }}
    >
      {/* Cyan layer (left offset) */}
      <div
        className="absolute inset-0 text-cyan-400"
        style={{
          transform: `translateX(${-rgbOffset}px)`,
          clipPath: `inset(${Math.abs(glitchOffset1)}px 0 ${Math.abs(glitchOffset2)}px 0)`,
          opacity: 0.7 * glitchIntensity,
        }}
      >
        {text}
      </div>

      {/* Magenta layer (right offset) */}
      <div
        className="absolute inset-0 text-fuchsia-500"
        style={{
          transform: `translateX(${rgbOffset}px)`,
          clipPath: `inset(${Math.abs(glitchOffset2)}px 0 ${Math.abs(glitchOffset1)}px 0)`,
          opacity: 0.7 * glitchIntensity,
        }}
      >
        {text}
      </div>

      {/* Main text with occasional slice */}
      <div
        style={{
          transform: `translateY(${sliceOffset * 0.3}px)`,
          clipPath:
            frame % 4 === 0
              ? `inset(${Math.abs(sliceOffset)}px 0 ${Math.abs(sliceOffset)}px 0)`
              : undefined,
        }}
      >
        <span className="text-white">{text}</span>
      </div>

      {/* Scanline effect */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `linear-gradient(
            transparent ${50 + glitchOffset1}%,
            rgba(0, 227, 170, 0.1) ${50 + glitchOffset1}%,
            rgba(0, 227, 170, 0.1) ${52 + glitchOffset1}%,
            transparent ${52 + glitchOffset1}%
          )`,
          opacity: glitchIntensity * 0.5,
        }}
      />
    </div>
  );
};

// ============================================================================
// CLI TABLE REVEAL - Row-by-row animation
// ============================================================================

/**
 * Renders a CLI-style table with row-by-row reveal animation.
 * Includes spring physics for natural motion.
 *
 * @example
 * ```tsx
 * <CLITableReveal
 *   headers={[
 *     { key: "NUMBER", width: 16 },
 *     { key: "TYPE", width: 10 },
 *     { key: "STATUS", width: 12 },
 *   ]}
 *   rows={[
 *     { NUMBER: "+1 555-0123", TYPE: "Local", STATUS: "Available" },
 *     { NUMBER: "+1 555-0456", TYPE: "Toll-free", STATUS: "Available" },
 *   ]}
 *   startFrame={85}
 *   rowDelay={8}
 *   accentColor="#00E3AA"
 * />
 * ```
 */
export const CLITableReveal: React.FC<CLITableRevealProps> = ({
  headers,
  rows,
  startFrame,
  rowDelay = 6,
  springConfig = { damping: 25, stiffness: 200, mass: 0.3 },
  accentColor = "#00E3AA",
  style,
}) => {
  const frame = useCurrentFrame();

  return (
    <div className="mt-3 text-left" style={style}>
      {/* Header */}
      <div
        className="text-xs font-bold"
        style={{
          color: accentColor,
          fontFamily: "JetBrains Mono, monospace",
          whiteSpace: "pre",
        }}
      >
        {headers.map((col) => (
          <span key={col.key}>{col.key.padEnd(col.width)}</span>
        ))}
      </div>

      {/* Separator */}
      <div
        className="my-1"
        style={{
          height: "1px",
          background: `linear-gradient(90deg, ${accentColor}66 0%, ${accentColor}1a 60%, transparent 100%)`,
        }}
      />

      {/* Rows with staggered animation */}
      {rows.map((row, index) => {
        const rowStartFrame = startFrame + index * rowDelay;

        const rowProgress = spring({
          frame: frame - rowStartFrame,
          fps: 30,
          config: springConfig,
        });

        const rowOpacity = interpolate(
          rowProgress,
          [0, 0.5, 1],
          [0, 0.7, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        if (frame < rowStartFrame) return null;

        return (
          <div
            key={index}
            className="text-xs py-0.5 text-left"
            style={{
              opacity: rowOpacity,
              color:
                index % 2 === 0
                  ? "rgba(255,255,255,0.95)"
                  : "rgba(255,255,255,0.75)",
              fontFamily: "JetBrains Mono, monospace",
              whiteSpace: "pre",
            }}
          >
            {headers.map((header, headerIndex) => (
              <span
                key={header.key}
                style={{
                  color:
                    headerIndex === headers.length - 1
                      ? accentColor
                      : undefined,
                }}
              >
                {(row[header.key] || "").padEnd(header.width)}
              </span>
            ))}
          </div>
        );
      })}

      {/* Summary line */}
      {frame >= startFrame + rows.length * rowDelay + 5 && (
        <div
          className="text-xs mt-2 text-left"
          style={{
            color: "rgba(255,255,255,0.5)",
            fontFamily: "JetBrains Mono, monospace",
            opacity: interpolate(
              frame,
              [
                startFrame + rows.length * rowDelay + 5,
                startFrame + rows.length * rowDelay + 10,
              ],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            ),
          }}
        >
          <span style={{ color: accentColor }}>✓</span> Found {rows.length}{" "}
          items
        </div>
      )}
    </div>
  );
};

// ============================================================================
// TERMINAL WINDOW - Spring-based slide-in
// ============================================================================

/**
 * Animated terminal window with traffic lights and title bar.
 * Slides in from the left with spring physics.
 *
 * @example
 * ```tsx
 * <TerminalWindow startFrame={30} title="my-app — bash">
 *   <div>npm install</div>
 * </TerminalWindow>
 * ```
 */
export const TerminalWindow: React.FC<TerminalWindowProps> = ({
  children,
  startFrame = 0,
  springConfig = { damping: 20, stiffness: 150, mass: 0.6 },
  title = "terminal — zsh — 80x24",
  className = "",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slide-in animation
  const slideProgress = spring({
    frame: frame - startFrame,
    fps,
    config: springConfig,
  });

  const translateX = interpolate(slideProgress, [0, 1], [-30, 0]);
  const opacity = interpolate(slideProgress, [0, 0.3, 1], [0, 0.8, 1]);

  // Subtle glow pulse
  const glowIntensity = interpolate(
    frame,
    [0, 30, 60],
    [0.2, 0.4, 0.2],
    { extrapolateRight: "loop" }
  );

  if (frame < startFrame) {
    return null;
  }

  return (
    <div
      className={`relative ${className}`}
      style={{
        transform: `translateX(${translateX}px)`,
        opacity,
        ...style,
      }}
    >
      {/* Outer glow */}
      <div
        className="absolute -inset-1 rounded-lg blur-xl"
        style={{
          background: `linear-gradient(135deg, rgba(0, 227, 170, ${glowIntensity}) 0%, transparent 50%, rgba(0, 227, 170, ${glowIntensity * 0.5}) 100%)`,
        }}
      />

      {/* Main window */}
      <div
        className="relative rounded-lg overflow-hidden text-left"
        style={{
          background: "rgba(8, 8, 8, 0.98)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(30, 30, 30, 0.9)",
          boxShadow: `
            0 20px 60px -15px rgba(0, 0, 0, 0.9),
            0 0 0 1px rgba(0, 227, 170, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.03)
          `,
        }}
      >
        {/* Title bar */}
        <div
          className="flex items-center gap-2 px-3 py-2"
          style={{
            background: "linear-gradient(180deg, rgba(18, 18, 18, 0.9) 0%, rgba(10, 10, 10, 0.9) 100%)",
            borderBottom: "1px solid rgba(30, 30, 30, 0.9)",
          }}
        >
          {/* Traffic lights */}
          <div className="flex gap-1.5">
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{
                background: "#FF5F56",
                boxShadow: "inset 0 0 0 0.5px rgba(0,0,0,0.2)",
              }}
            />
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{
                background: "#FFBD2E",
                boxShadow: "inset 0 0 0 0.5px rgba(0,0,0,0.2)",
              }}
            />
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{
                background: "#27C93F",
                boxShadow: "inset 0 0 0 0.5px rgba(0,0,0,0.2)",
              }}
            />
          </div>

          {/* Window title */}
          <div className="flex-1 pl-3">
            <span
              className="text-xs font-mono"
              style={{ color: "rgba(255, 255, 255, 0.35)" }}
            >
              {title}
            </span>
          </div>
        </div>

        {/* Content area */}
        <div
          className="p-5 font-mono text-sm text-left"
          style={{
            background: "linear-gradient(180deg, rgba(5, 5, 5, 0.8) 0%, rgba(5, 5, 5, 0.6) 100%)",
            minHeight: "280px",
            lineHeight: "1.6",
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// SUCCESS CHECK - Animated checkmark
// ============================================================================

export interface SuccessCheckProps {
  /** Frame to start animation */
  startFrame: number;
  /** Message to display (default: "Success") */
  message?: string;
  /** Primary color (default: #00E3AA) */
  color?: string;
  style?: React.CSSProperties;
}

/**
 * Animated success checkmark with spring physics.
 * Shows a check icon with stroke animation.
 *
 * @example
 * ```tsx
 * <SuccessCheck
 *   startFrame={175}
 *   message="Message sent successfully"
 *   color="#00E3AA"
 * />
 * ```
 */
export const SuccessCheck: React.FC<SuccessCheckProps> = ({
  startFrame,
  message = "Success",
  color = "#00E3AA",
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: {
      damping: 15,
      stiffness: 180,
      mass: 0.4,
    },
  });

  const scale = interpolate(progress, [0, 1], [0.5, 1]);
  const opacity = interpolate(progress, [0, 0.3, 1], [0, 1, 1]);
  const strokeOffset = interpolate(progress, [0, 1], [12, 0]);

  if (frame < startFrame) return null;

  return (
    <div
      className="flex items-center gap-2 mt-3 text-left"
      style={{
        transform: `scale(${scale})`,
        opacity,
        transformOrigin: "left center",
        ...style,
      }}
    >
      <div
        className="flex items-center justify-center w-4 h-4 rounded-full"
        style={{
          background: color,
          color: "#050505",
          boxShadow: `0 0 10px ${color}66`,
        }}
      >
        <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
          <path
            d="M2 6L5 9L10 3"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="12"
            strokeDashoffset={strokeOffset}
          />
        </svg>
      </div>
      <span className="text-sm" style={{ color }}>
        {message}
      </span>
    </div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export { TerminalZoom, TerminalPan, AsciiReveal, TypewriterText, GlitchText, CLITableReveal, TerminalWindow, SuccessCheck };
export default TerminalMotion;
