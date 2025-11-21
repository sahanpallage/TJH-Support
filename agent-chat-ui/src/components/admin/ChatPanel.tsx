"use client";

import { useState, useRef, useEffect } from "react";
import { GripVertical, Paperclip, X } from "lucide-react";
import {
  useAdminChat,
  type Conversation,
  type Message,
} from "@/contexts/AdminChatContext";
import { MarkdownText } from "@/components/thread/markdown-text";
import "@/components/admin/chat-markdown.css";

// Supported file types
const SUPPORTED_FILE_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // .docx
  "application/msword", // .doc
  "text/plain",
  "text/markdown",
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

type UploadedFile = {
  id: string;
  file: File;
  preview?: string;
};

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
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setShowChatPanel, sendMessage, isSending } = useAdminChat();
  const containerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef<number>(0);
  const startWidthRef = useRef<number>(width);

  // Debug: Log component render and feature availability
  useEffect(() => {
    console.log("[ChatPanel] Component rendered", {
      conversationId: conversation?.id,
      messagesCount: messages.length,
      uploadedFilesCount: uploadedFiles.length,
      timestamp: new Date().toISOString(),
    });
    console.log("[ChatPanel] File upload feature loaded:", {
      supportedTypes: SUPPORTED_FILE_TYPES,
      maxFileSize: MAX_FILE_SIZE,
    });
  }, [conversation?.id, messages.length, uploadedFiles.length]);

  // Debug: Log when file input is available
  useEffect(() => {
    if (fileInputRef.current) {
      console.log("[ChatPanel] File input element mounted");
    }
  }, []);

  // Track typing state for agent messages
  const [typingMessage, setTypingMessage] = useState<{
    id: number;
    fullText: string;
    displayedText: string;
  } | null>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastAgentMessageIdRef = useRef<number | null>(null);

  // Update startWidthRef when width prop changes
  useEffect(() => {
    if (!isDragging) {
      startWidthRef.current = width;
    }
  }, [width, isDragging]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending, typingMessage]);

  // Handle typing animation for new agent messages
  const prevIsSendingRef = useRef(isSending);
  const processedMessageIdsRef = useRef<Set<number>>(new Set());

  useEffect(() => {
    // Trigger typing animation when we transition from sending to not sending
    // OR when a new agent message appears that we haven't processed yet
    const sendingCompleted = prevIsSendingRef.current && !isSending;

    if (sendingCompleted || !isSending) {
      // Find the last agent message
      const lastAgentMessage = messages
        .filter((m) => m.author === "agent")
        .sort((a, b) => b.id - a.id)[0];

      if (
        lastAgentMessage &&
        !processedMessageIdsRef.current.has(lastAgentMessage.id) &&
        !typingMessage // Don't start new animation if one is already running
      ) {
        // Mark this message as being processed
        processedMessageIdsRef.current.add(lastAgentMessage.id);
        lastAgentMessageIdRef.current = lastAgentMessage.id;

        // Start typing animation immediately
        setTypingMessage({
          id: lastAgentMessage.id,
          fullText: lastAgentMessage.text,
          displayedText: "",
        });
      }
    }

    prevIsSendingRef.current = isSending;

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [messages, isSending, typingMessage]);

  // Typing animation effect
  useEffect(() => {
    if (!typingMessage) return;

    const fullText = typingMessage.fullText;
    const currentLength = typingMessage.displayedText.length;

    if (currentLength < fullText.length) {
      // Calculate typing speed - type faster for better UX
      // Type word by word for natural feel, character by character for punctuation
      const remainingText = fullText.slice(currentLength);
      const nextSpaceIndex = remainingText.indexOf(" ");
      const nextNewlineIndex = remainingText.indexOf("\n");

      // Determine how many characters to add
      let charsToAdd = 1;
      if (nextSpaceIndex !== -1 && nextSpaceIndex < 5) {
        // If next word is close, type the whole word
        charsToAdd = nextSpaceIndex + 1;
      } else if (nextNewlineIndex !== -1 && nextNewlineIndex < 3) {
        // If next newline is close, type to newline
        charsToAdd = nextNewlineIndex + 1;
      }

      // Adjust speed: faster for words, slower for punctuation
      const isPunctuation = /[.,!?;:]/.test(remainingText[0]);
      const delay = isPunctuation ? 80 : 25; // Slight pause at punctuation, visible typing speed

      typingTimeoutRef.current = setTimeout(() => {
        setTypingMessage({
          ...typingMessage,
          displayedText: fullText.slice(0, currentLength + charsToAdd),
        });
      }, delay);
    } else {
      // Typing complete, clear after a brief moment
      typingTimeoutRef.current = setTimeout(() => {
        setTypingMessage(null);
      }, 200);
    }

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [typingMessage]);

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

  // Handle file selection
  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) {
      console.log("[ChatPanel] No files selected");
      return;
    }

    console.log("[ChatPanel] Files selected:", {
      count: files.length,
      files: Array.from(files).map((f) => ({
        name: f.name,
        type: f.type,
        size: f.size,
      })),
    });

    const newFiles: UploadedFile[] = [];
    const errors: string[] = [];

    Array.from(files).forEach((file) => {
      // Check file type
      const isValidType =
        SUPPORTED_FILE_TYPES.includes(file.type) ||
        file.name.endsWith(".docx") ||
        file.name.endsWith(".doc") ||
        file.name.endsWith(".txt") ||
        file.name.endsWith(".md");

      if (!isValidType) {
        errors.push(
          `${file.name}: Unsupported file type. Supported: PDF, DOCX, DOC, TXT, MD, or images (JPEG, PNG, GIF, WEBP)`,
        );
        return;
      }

      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large. Maximum size is 10MB.`);
        return;
      }

      // Create preview for images
      const fileId = `${Date.now()}-${Math.random()}`;
      const uploadedFile: UploadedFile = { id: fileId, file };

      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? { ...f, preview: e.target?.result as string }
                : f,
            ),
          );
        };
        reader.readAsDataURL(file);
      }

      newFiles.push(uploadedFile);
    });

    if (errors.length > 0) {
      console.error("[ChatPanel] File upload errors:", errors);
      alert(errors.join("\n"));
    }

    if (newFiles.length > 0) {
      setUploadedFiles((prev) => [...prev, ...newFiles]);
      console.log("[ChatPanel] Files added:", newFiles.length);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  // Remove file from upload list
  function handleRemoveFile(fileId: string) {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
    console.log("[ChatPanel] File removed:", fileId);
  }

  // Format file size
  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  // Get file type icon/text
  function getFileTypeLabel(file: File): string {
    if (file.type === "application/pdf") return "PDF";
    if (
      file.type ===
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
      file.name.endsWith(".docx")
    )
      return "DOCX";
    if (file.type === "application/msword" || file.name.endsWith(".doc"))
      return "DOC";
    if (file.type === "text/plain" || file.name.endsWith(".txt")) return "TXT";
    if (file.type === "text/markdown" || file.name.endsWith(".md")) return "MD";
    if (file.type.startsWith("image/")) return "IMAGE";
    return "FILE";
  }

  async function handleSubmit() {
    const text = input.trim();
    if (!conversation) return;

    // Require either text or files
    if (!text && uploadedFiles.length === 0) return;

    console.log("[ChatPanel] Submitting message", {
      hasText: !!text,
      filesCount: uploadedFiles.length,
    });

    // For now, send text message with file info
    // TODO: Implement actual file upload to backend
    let messageText = text;
    if (uploadedFiles.length > 0) {
      const fileList = uploadedFiles
        .map((f) => `[File: ${f.file.name} (${formatFileSize(f.file.size)})]`)
        .join("\n");
      messageText = messageText
        ? `${messageText}\n\n${fileList}`
        : `Uploaded ${uploadedFiles.length} file(s):\n${fileList}`;
    }

    setInput("");
    setUploadedFiles([]);
    await sendMessage(conversation.id, messageText);
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
            {messages.map((m) => {
              // Check if this message is currently being typed
              const isTyping = typingMessage?.id === m.id;
              const displayText =
                isTyping && typingMessage
                  ? typingMessage.displayedText
                  : m.text;
              const showCursor =
                isTyping &&
                typingMessage &&
                typingMessage.displayedText.length <
                  typingMessage.fullText.length;

              return (
                <div
                  key={m.id}
                  className={`max-w-[90%] rounded-lg px-4 py-3 ${
                    m.author === "admin"
                      ? "ml-auto bg-sky-600 text-white"
                      : "mr-auto bg-slate-100 text-slate-800"
                  }`}
                >
                  {m.author === "agent" ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                      {displayText && displayText.length > 0 ? (
                        <div className="space-y-1">
                          <MarkdownText>{displayText}</MarkdownText>
                          {showCursor && (
                            <span className="ml-1 inline-block h-4 w-0.5 animate-pulse bg-slate-600 align-middle" />
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-500">...</span>
                      )}
                    </div>
                  ) : (
                    <p className="break-words whitespace-pre-wrap text-white">
                      {m.text}
                    </p>
                  )}
                </div>
              );
            })}
            {isSending && !typingMessage && (
              <div className="mr-auto max-w-[90%] rounded-lg bg-slate-100 px-3 py-2 text-slate-800">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
                  </div>
                  <span className="text-xs text-slate-500 italic">
                    Agent is thinking...
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* input */}
      <div className="border-t border-slate-200 bg-white p-4">
        {/* DEBUG: Test element to verify rendering - FORCE VISIBLE */}
        <div
          className="mb-2 border-2 border-yellow-500 bg-yellow-200 p-2 text-xs font-bold"
          style={
            {
              display: "block",
              visibility: "visible",
              zIndex: 9999,
            } as React.CSSProperties
          }
        >
          🚨 DEBUG: File upload feature v2 - {new Date().toISOString()}
        </div>
        {/* File previews */}
        {uploadedFiles.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {uploadedFiles.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="group relative flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-2 py-1.5 text-xs"
              >
                {uploadedFile.preview ? (
                  <img
                    src={uploadedFile.preview}
                    alt={uploadedFile.file.name}
                    className="h-8 w-8 rounded object-cover"
                  />
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded bg-slate-200 text-[10px] font-medium text-slate-600">
                    {getFileTypeLabel(uploadedFile.file)}
                  </div>
                )}
                <div className="flex flex-col">
                  <span className="max-w-[120px] truncate font-medium text-slate-700">
                    {uploadedFile.file.name}
                  </span>
                  <span className="text-[10px] text-slate-500">
                    {formatFileSize(uploadedFile.file.size)}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(uploadedFile.id)}
                  className="ml-1 flex h-5 w-5 items-center justify-center rounded text-slate-400 opacity-0 transition-opacity group-hover:opacity-100 hover:bg-slate-200 hover:text-slate-600"
                  aria-label="Remove file"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        <form
          className="mx-auto flex max-w-full items-end gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm transition-shadow focus-within:border-sky-300 focus-within:shadow-md"
          onSubmit={async (e) => {
            e.preventDefault();
            await handleSubmit();
          }}
        >
          {/* Hidden file input */}
          <input
            ref={(el) => {
              fileInputRef.current = el;
              if (el) {
                console.log("[ChatPanel] File input mounted", el.id);
              }
            }}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.md,image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload-input"
          />

          {/* File upload button - FORCE VISIBLE FOR DEBUGGING */}
          <label
            htmlFor="file-upload-input"
            className="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-lg border-2 border-red-500 bg-red-100 text-red-600 transition-colors hover:bg-red-200 hover:text-red-700"
            aria-label="Upload file"
            title="Upload PDF, DOCX, Text, or Image"
            style={
              {
                display: "flex",
                visibility: "visible",
                opacity: 1,
                minWidth: "32px",
                minHeight: "32px",
              } as React.CSSProperties
            }
            ref={(el) => {
              if (el) {
                console.log("[ChatPanel] Upload button label mounted", {
                  htmlFor: el.htmlFor,
                  hasPaperclip: !!el.querySelector("svg"),
                  children: Array.from(el.children).map((c) => c.tagName),
                });
                // Force visibility
                el.style.display = "flex";
                el.style.visibility = "visible";
                el.style.opacity = "1";
              }
            }}
          >
            <Paperclip
              className="h-4 w-4"
              style={{
                display: "block",
                width: "16px",
                height: "16px",
                flexShrink: 0,
              }}
            />
          </label>

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
            disabled={
              (!input.trim() && uploadedFiles.length === 0) || isSending
            }
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
