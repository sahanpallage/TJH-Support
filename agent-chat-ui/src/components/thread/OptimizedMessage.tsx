/**
 * Optimized Message Component
 * Wraps message components with React.memo for performance
 * Prevents unnecessary re-renders when parent updates
 */

import React, { memo } from "react";
import { Message, Checkpoint } from "@langchain/langgraph-sdk";
import { AssistantMessage, AssistantMessageLoading } from "./messages/ai";
import { HumanMessage } from "./messages/human";

interface OptimizedMessageProps {
  message?: Message;
  isLoading?: boolean;
  handleRegenerate?: (parentCheckpoint: Checkpoint | null | undefined) => void;
  isLoadingMessage?: boolean;
  type?: "ai" | "human";
  isLoadingState?: boolean;
}

/**
 * Memoized AI Message - only re-renders if props actually change
 */
export const OptimizedAIMessage = memo(
  ({
    message,
    isLoading = false,
    handleRegenerate = () => {},
  }: Omit<OptimizedMessageProps, "type" | "isLoadingMessage">) => (
    <AssistantMessage
      message={message}
      isLoading={isLoading}
      handleRegenerate={handleRegenerate}
    />
  ),
  (prevProps, nextProps) => {
    // Return true to skip re-render (props are equal), false to re-render
    if (prevProps.message?.id !== nextProps.message?.id) return false;
    if (
      JSON.stringify(prevProps.message?.content) !==
      JSON.stringify(nextProps.message?.content)
    ) {
      return false;
    }
    if (prevProps.isLoading !== nextProps.isLoading) return false;
    // All props are equal, skip re-render
    return true;
  },
);

OptimizedAIMessage.displayName = "OptimizedAIMessage";

/**
 * Memoized Human Message - only re-renders if props actually change
 */
export const OptimizedHumanMessage = memo(
  ({
    message,
    isLoading = false,
  }: Pick<OptimizedMessageProps, "message" | "isLoading">) => {
    if (!message) return null;
    return (
      <HumanMessage
        message={message}
        isLoading={isLoading}
      />
    );
  },
  (prevProps, nextProps) => {
    // Return true to skip re-render (props are equal), false to re-render
    if (prevProps.message?.id !== nextProps.message?.id) return false;
    if (
      JSON.stringify(prevProps.message?.content) !==
      JSON.stringify(nextProps.message?.content)
    ) {
      return false;
    }
    if (prevProps.isLoading !== nextProps.isLoading) return false;
    // All props are equal, skip re-render
    return true;
  },
);

OptimizedHumanMessage.displayName = "OptimizedHumanMessage";

/**
 * Memoized Loading Message
 */
export const OptimizedLoadingMessage = memo(() => <AssistantMessageLoading />);

OptimizedLoadingMessage.displayName = "OptimizedLoadingMessage";

/**
 * Universal Message Component - automatically chooses optimized version
 */
export const OptimizedMessage = memo(
  ({
    message,
    isLoading = false,
    handleRegenerate = () => {},
    isLoadingMessage = false,
    type,
  }: OptimizedMessageProps) => {
    if (isLoadingMessage) {
      return <OptimizedLoadingMessage />;
    }

    const messageType = type || message?.type;

    if (messageType === "human") {
      return <OptimizedHumanMessage message={message} />;
    }

    return (
      <OptimizedAIMessage
        message={message}
        isLoading={isLoading}
        handleRegenerate={handleRegenerate}
      />
    );
  },
  (prevProps, nextProps) => {
    // Quick bailout for loading state changes
    if (prevProps.isLoadingMessage !== nextProps.isLoadingMessage) return false;

    // Compare message identity
    if (prevProps.message?.id !== nextProps.message?.id) return false;

    // Compare message content
    if (
      JSON.stringify(prevProps.message?.content) !==
      JSON.stringify(nextProps.message?.content)
    ) {
      return false;
    }

    // Compare loading state
    if (prevProps.isLoading !== nextProps.isLoading) return false;

    // Compare type
    if (prevProps.type !== nextProps.type) return false;

    // No changes, skip re-render
    return true;
  },
);

OptimizedMessage.displayName = "OptimizedMessage";

export default OptimizedMessage;
