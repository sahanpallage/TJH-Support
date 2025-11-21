"use client";

import { useEffect, useState, memo } from "react";
import { MarkdownText } from "./markdown-text";

interface TypingAnimationProps {
  text: string;
  isComplete: boolean;
  speed?: number; // milliseconds per character
}

/**
 * Typing Animation Component
 * Displays text with a visual streaming animation
 * When isComplete is false, shows text with typing indicator
 * When isComplete is true, shows the full rendered text
 */
const TypingAnimationImpl = ({
  text,
  isComplete,
  speed = 8,
}: TypingAnimationProps) => {
  const [displayedText, setDisplayedText] = useState("");
  const [showResponding, setShowResponding] = useState(false);

  useEffect(() => {
    if (isComplete) {
      setDisplayedText(text);
      setShowResponding(false);
      return;
    }

    setDisplayedText("");
    const timer = setTimeout(() => setShowResponding(true), 500); // Delay before showing "AI is responding"

    let index = 0;
    const intervalId = setInterval(() => {
      setDisplayedText((prev) => prev + text[index]);
      index++;
      if (index === text.length) {
        clearInterval(intervalId);
        setShowResponding(false);
      }
    }, speed);

    return () => {
      clearTimeout(timer);
      clearInterval(intervalId);
    };
  }, [text, isComplete, speed]);

  return (
    <div className="min-h-[28px] w-full py-1">
      {displayedText && <MarkdownText>{displayedText}</MarkdownText>}
      {/* Show animated typing indicator while streaming */}
      {showResponding && (
        <div className="mt-2 flex items-center gap-1">
          <span className="text-xs text-gray-500">AI is responding</span>
          <div className="flex gap-0.5">
            <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500"></span>
            <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500 delay-100"></span>
            <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500 delay-200"></span>
          </div>
        </div>
      )}
    </div>
  );
};

export const TypingAnimation = memo(TypingAnimationImpl);
