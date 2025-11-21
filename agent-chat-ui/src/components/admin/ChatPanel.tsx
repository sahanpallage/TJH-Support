"use client";

import { useState, useRef, useEffect } from "react";
import { GripVertical } from "lucide-react";
import {
  useAdminChat,
  type Conversation,
  type Message,
} from "@/contexts/AdminChatContext";

export function ChatPanel({
  conversation,
  messages,
  width = 320,
  onWidthChange,
}: {
  conversation: Conversation | null;
  messages: Message[];
  width?: number;
  onWidthChange?: (width: number) => void;
}) {
  const [input, setInput] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const { setShowChatPanel, sendMessage, isSending } = useAdminChat();
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef<number>(0);
  const startWidthRef = useRef<number>(width);

  // Update startWidthRef when width prop changes
  useEffect(() => {
    if (!isDragging) {
      startWidthRef.current = width;
    }
  }, [width, isDragging]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!containerRef.current || !onWidthChange) return;

    setIsDragging(true);
    startXRef.current = e.clientX;
    startWidthRef.current = width;

    // Prevent text selection while dragging
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";
  };

  useEffect(() => {
    if (!isDragging || !onWidthChange) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const deltaX = startXRef.current - e.clientX; // Negative when dragging left (making wider)
      const newWidth = startWidthRef.current + deltaX;

      // Constrain width between min and max
      const minWidth = 280;
      const maxWidth = 800;
      const constrainedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
      onWidthChange(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    };
  }, [isDragging, onWidthChange, width]);

  if (!conversation) {
    return (
      <div
        ref={containerRef}
        className="relative flex h-full w-full flex-col"
      >
        {/* Resize handle on the left */}
        {onWidthChange && (
          <div
            onMouseDown={handleMouseDown}
            onClick={(e) => e.stopPropagation()}
            className={`group absolute top-0 left-0 z-10 h-full w-2 cursor-col-resize transition-colors select-none ${
              isDragging ? "bg-sky-500" : "bg-transparent hover:bg-sky-400"
            }`}
            title="Drag to resize chat panel"
            style={{ touchAction: "none" }}
          >
            <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100">
              <GripVertical className="h-5 w-5 text-sky-500" />
            </div>
          </div>
        )}
        <div className="flex items-center justify-end border-b border-slate-200 px-4 py-3">
          <button
            onClick={() => setShowChatPanel(false)}
            className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close chat panel"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-4 w-4"
            >
              <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
            </svg>
          </button>
        </div>
        <div className="flex flex-1 items-center justify-center px-4 text-center text-xs text-slate-400">
          Select a conversation to start chatting with the agent.
        </div>
      </div>
    );
  }

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  async function handleSubmit() {
    const text = input.trim();
    if (!text || !conversation) return;

    setInput("");
    await sendMessage(conversation.id, text);
  }

  return (
    <div
      ref={containerRef}
      className="relative flex h-full w-full flex-col"
    >
      {/* Resize handle on the left */}
      {onWidthChange && (
        <div
          onMouseDown={handleMouseDown}
          onClick={(e) => e.stopPropagation()}
          className={`group absolute top-0 left-0 z-10 h-full w-2 cursor-col-resize transition-colors select-none ${
            isDragging ? "bg-sky-500" : "bg-transparent hover:bg-sky-400"
          }`}
          title="Drag to resize chat panel"
          style={{ touchAction: "none" }}
        >
          <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100">
            <GripVertical className="h-5 w-5 text-sky-500" />
          </div>
        </div>
      )}
      {/* header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div>
          <p className="text-xs font-semibold text-slate-700">
            {conversation.title}
          </p>
          <p className="text-[11px] text-slate-500">
            Chat with TJH AI Assistant
          </p>
        </div>
        <button
          onClick={() => setShowChatPanel(false)}
          className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
          aria-label="Close chat panel"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="h-4 w-4"
          >
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
          </svg>
        </button>
      </div>

      {/* messages */}
      <div className="flex-1 space-y-2 overflow-y-auto scroll-smooth px-4 py-3 text-xs">
        {messages.length === 0 && !isSending ? (
          <div className="flex h-full items-center justify-center text-slate-400">
            <p className="text-xs">No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <>
            {messages.map((m) => (
              <div
                key={m.id}
                className={`max-w-[90%] rounded-lg px-3 py-2 ${
                  m.author === "admin"
                    ? "ml-auto bg-sky-600 text-white"
                    : "mr-auto bg-slate-100 text-slate-800"
                }`}
              >
                {m.text}
              </div>
            ))}
            {isSending && (
              <div className="mr-auto max-w-[90%] rounded-lg bg-slate-100 px-3 py-2 text-slate-800">
                <span className="text-xs text-slate-500 italic">
                  Agent is typing...
                </span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* input */}
      <div className="border-t border-slate-200 bg-white p-4">
        <form
          className="mx-auto flex max-w-full items-end gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm transition-shadow focus-within:border-sky-300 focus-within:shadow-md"
          onSubmit={async (e) => {
            e.preventDefault();
            await handleSubmit();
          }}
        >
          <textarea
            className="max-h-32 flex-1 resize-none border-0 bg-transparent px-2 py-1.5 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none"
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={async (e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                await handleSubmit();
              }
            }}
            rows={1}
            style={{
              height: "auto",
              minHeight: "24px",
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = "auto";
              target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
            }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isSending}
            className="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-lg bg-sky-600 text-white transition-colors hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:opacity-50"
            aria-label="Send message"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="h-4 w-4"
            >
              <path d="M3.105 2.289a.75.75 0 00-.826.95l1.414 4.925A1.5 1.5 0 005.135 9.25h6.115a.75.75 0 010 1.5H5.135a1.5 1.5 0 00-1.442 1.086l-1.414 4.926a.75.75 0 00.826.95 28.896 28.896 0 0015.293-7.154.75.75 0 000-1.115A28.897 28.897 0 003.105 2.289z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
