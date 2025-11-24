"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";

interface TypingTextProps {
  text: string;
  speed?: number; // Characters per second
  delay?: number; // Delay before starting (ms)
  onComplete?: () => void;
  className?: string;
  showCursor?: boolean;
}

export default function TypingText({
  text,
  speed = 30, // 30 characters per second = fast, readable
  delay = 0,
  onComplete,
  className = "",
  showCursor = true,
}: TypingTextProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    // Delay before starting
    if (delay > 0 && !hasStarted) {
      const startTimer = setTimeout(() => {
        setHasStarted(true);
      }, delay);
      return () => clearTimeout(startTimer);
    } else {
      setHasStarted(true);
    }
  }, [delay, hasStarted]);

  useEffect(() => {
    if (!hasStarted || isComplete || currentIndex >= text.length) {
      if (currentIndex >= text.length && !isComplete) {
        setIsComplete(true);
        onComplete?.();
      }
      return;
    }

    const intervalMs = 1000 / speed;
    const timer = setTimeout(() => {
      setDisplayedText(text.slice(0, currentIndex + 1));
      setCurrentIndex(currentIndex + 1);
    }, intervalMs);

    return () => clearTimeout(timer);
  }, [currentIndex, text, speed, isComplete, hasStarted, onComplete]);

  return (
    <span className={`font-mono ${className}`}>
      {displayedText}
      {showCursor && !isComplete && (
        <motion.span
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="inline-block ml-1"
        >
          _
        </motion.span>
      )}
    </span>
  );
}

/**
 * Typing effect for multi-line text with terminal styling
 */
export function TerminalTyping({
  lines,
  speed = 30,
  lineDelay = 100, // Delay between lines
  className = "",
}: {
  lines: string[];
  speed?: number;
  lineDelay?: number;
  className?: string;
}) {
  const [currentLine, setCurrentLine] = useState(0);

  return (
    <div className={`font-mono ${className}`}>
      {lines.map((line, index) => (
        <div key={index} className="mb-2">
          {index <= currentLine && (
            <TypingText
              text={line}
              speed={speed}
              delay={index * lineDelay}
              showCursor={index === currentLine}
              onComplete={() => {
                if (index < lines.length - 1) {
                  setTimeout(() => setCurrentLine(index + 1), lineDelay);
                }
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Blinking cursor effect (static)
 */
export function BlinkingCursor({ className = "" }: { className?: string }) {
  return (
    <motion.span
      animate={{ opacity: [1, 0, 1] }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className={`inline-block ${className}`}
    >
      _
    </motion.span>
  );
}

/**
 * Terminal prompt with blinking cursor
 */
export function TerminalPrompt({
  prefix = "$",
  children,
}: {
  prefix?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="font-mono flex items-center space-x-2">
      <span className="text-terminal-gray">{prefix}</span>
      {children}
      <BlinkingCursor />
    </div>
  );
}
