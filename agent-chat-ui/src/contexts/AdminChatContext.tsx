"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/* ---------- TYPES ---------- */

export type Conversation = {
  id: number;
  customer_id: number;
  title: string;
  external_thread_id: string;
  created_at: string;
};

export type Message = {
  id: number;
  conversation_id: number;
  author: "admin" | "agent";
  text: string;
  created_at: string;
};

type AdminChatContextType = {
  showChatPanel: boolean;
  setShowChatPanel: (show: boolean) => void;

  conversations: Conversation[];
  selectedConversationId: number | null;
  setSelectedConversationId: (id: number | null) => void;

  messages: Message[]; // all messages, filtered per conversation where needed
  sendMessage: (
    conversationId: number,
    text: string,
    files?: File[],
  ) => Promise<void>;
  createConversation: (title?: string) => Promise<Conversation | null>;
  deleteConversation: (conversationId: number) => Promise<void>;
  isSending: boolean;
};

const AdminChatContext = createContext<AdminChatContextType | undefined>(
  undefined,
);

/* ---------- PROVIDER ---------- */

export function AdminChatProvider({ children }: { children: ReactNode }) {
  const [showChatPanel, setShowChatPanel] = useState(false);

  const [customerId, setCustomerId] = useState<number | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<
    number | null
  >(null);

  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);

  // -------- bootstrap: ensure customer exists + load conversations --------
  useEffect(() => {
    async function bootstrap() {
      try {
        // 1) get or create Annabelle as a "demo" customer
        const customersRes = await fetch(`${API_BASE}/customers/`);
        const customers = await customersRes.json();

        let customer = customers.find(
          (c: any) => c.email === "annabelle.garcia@example.com",
        );

        if (!customer) {
          const createRes = await fetch(`${API_BASE}/customers/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              full_name: "Annabelle Garcia",
              email: "annabelle.garcia@example.com",
              title: "Chief of Staff, Business Operations Manager",
              location: "New York, USA",
            }),
          });
          customer = await createRes.json();
        }

        setCustomerId(customer.id);

        // 2) load conversations for this customer
        const convRes = await fetch(
          `${API_BASE}/conversations/customer/${customer.id}`,
        );
        const convData: Conversation[] = await convRes.json();
        setConversations(convData);

        if (convData.length > 0) {
          setSelectedConversationId(convData[0].id);
          // Load messages for the first conversation
          await loadMessages(convData[0].id);
        }
      } catch (err) {
        console.error("Failed to bootstrap admin chat context", err);
      }
    }

    bootstrap();
  }, []);

  // Load messages when conversation selection changes
  useEffect(() => {
    if (selectedConversationId !== null) {
      loadMessages(selectedConversationId).catch(console.error);
    } else {
      setMessages([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedConversationId]);

  // Function to load messages from backend with retry logic
  async function loadMessages(
    conversationId: number,
    retries: number = 3,
    delay: number = 300,
  ): Promise<void> {
    setIsLoadingMessages(true);

    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        // Add cache-busting timestamp to prevent browser caching
        const timestamp = Date.now();
        const res = await fetch(
          `${API_BASE}/messages/conversation/${conversationId}?t=${timestamp}`,
          {
            method: "GET",
            headers: {
              "Cache-Control": "no-cache, no-store, must-revalidate",
              Pragma: "no-cache",
              Expires: "0",
            },
          },
        );

        if (!res.ok) {
          if (attempt < retries - 1) {
            // Wait before retrying with exponential backoff
            await new Promise((resolve) =>
              setTimeout(resolve, delay * Math.pow(2, attempt)),
            );
            continue;
          }
          console.error("Failed to load messages", res.status);
          setMessages([]);
          return;
        }

        const data: Message[] = await res.json();
        // Use requestAnimationFrame for smooth cross-browser updates
        if (typeof window !== "undefined") {
          requestAnimationFrame(() => {
            setMessages(data);
          });
        } else {
          setMessages(data);
        }
        return;
      } catch (err) {
        if (attempt < retries - 1) {
          // Wait before retrying
          await new Promise((resolve) =>
            setTimeout(resolve, delay * Math.pow(2, attempt)),
          );
          continue;
        }
        console.error("Error loading messages", err);
        setMessages([]);
      } finally {
        setIsLoadingMessages(false);
      }
    }
  }

  // -------- sendMessage: frontend → FastAPI → JobProMax agent --------
  async function sendMessage(
    conversationId: number,
    text: string,
    files?: File[],
  ) {
    // Require either text or files
    if (!text.trim() && (!files || files.length === 0)) return;

    // Build message text for display
    const displayText = text.trim() || "[Files attached]";

    // Optimistic update: show admin message immediately
    const tempAdminMessage: Message = {
      id: -1, // Temporary ID
      conversation_id: conversationId,
      author: "admin",
      text: displayText,
      created_at: new Date().toISOString(),
    };

    // Add optimistic message immediately for smooth UX
    setMessages((prev) => [...prev, tempAdminMessage]);

    setIsSending(true);
    try {
      // Add cache-busting to prevent browser caching
      const timestamp = Date.now();

      let res: Response;

      // If files are provided, use FormData; otherwise use JSON
      if (files && files.length > 0) {
        const formData = new FormData();
        formData.append("message", text.trim() || "");

        // Append all files
        for (const file of files) {
          formData.append("files", file);
        }

        res = await fetch(
          `${API_BASE}/chat/conversations/${conversationId}/messages?t=${timestamp}`,
          {
            method: "POST",
            headers: {
              "Cache-Control": "no-cache, no-store, must-revalidate",
              Pragma: "no-cache",
              Expires: "0",
              // Don't set Content-Type for FormData - browser will set it with boundary
            },
            body: formData,
          },
        );
      } else {
        // No files, use JSON (backward compatible)
        res = await fetch(
          `${API_BASE}/chat/conversations/${conversationId}/messages?t=${timestamp}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Cache-Control": "no-cache, no-store, must-revalidate",
              Pragma: "no-cache",
              Expires: "0",
            },
            body: JSON.stringify({ message: text }),
          },
        );
      }

      if (!res.ok) {
        // Remove optimistic message on error
        setMessages((prev) =>
          prev.filter((m) => m.id !== -1 || m.text !== text.trim()),
        );
        console.error(
          "Failed to send chat message",
          res.status,
          await res.text(),
        );
        return;
      }

      const data = await res.json();

      // If backend returns messages, use them directly (faster and more reliable)
      if (
        data.messages &&
        Array.isArray(data.messages) &&
        data.messages.length > 0
      ) {
        // Use requestAnimationFrame for smooth cross-browser updates
        if (typeof window !== "undefined") {
          requestAnimationFrame(() => {
            setMessages((prev) => {
              // Remove optimistic message and add real messages
              const filtered = prev.filter(
                (m) => !(m.id === -1 && m.text === text.trim()),
              );
              return [...filtered, ...data.messages];
            });
          });
        } else {
          setMessages((prev) => {
            const filtered = prev.filter(
              (m) => !(m.id === -1 && m.text === text.trim()),
            );
            return [...filtered, ...data.messages];
          });
        }
      } else {
        // Fallback: reload messages if backend doesn't return them
        // Use a small delay to ensure database commit is propagated
        await new Promise((resolve) => setTimeout(resolve, 100));
        await loadMessages(conversationId);
      }
    } catch (err) {
      // Remove optimistic message on error
      setMessages((prev) =>
        prev.filter((m) => !(m.id === -1 && m.text === text.trim())),
      );
      console.error("Error talking to chat backend", err);
    } finally {
      setIsSending(false);
    }
  }

  async function createConversation(title?: string) {
    if (!customerId) {
      console.error("Cannot create conversation without a customer");
      return null;
    }

    const trimmedTitle =
      title?.trim() || `Conversation ${conversations.length + 1}`;
    try {
      const res = await fetch(`${API_BASE}/conversations/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: customerId,
          title: trimmedTitle,
        }),
      });

      if (!res.ok) {
        console.error(
          "Failed to create conversation",
          res.status,
          await res.text(),
        );
        return null;
      }

      const newConversation: Conversation = await res.json();
      setConversations((prev) => [newConversation, ...prev]);
      setSelectedConversationId(newConversation.id);
      setShowChatPanel(true);
      // Load messages for the new conversation (will be empty initially)
      await loadMessages(newConversation.id);
      return newConversation;
    } catch (err) {
      console.error("Error creating conversation", err);
      return null;
    }
  }

  async function deleteConversation(conversationId: number) {
    try {
      const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        console.error(
          "Failed to delete conversation",
          res.status,
          await res.text(),
        );
        return;
      }

      setConversations((prev) => {
        const updated = prev.filter(
          (conversation) => conversation.id !== conversationId,
        );

        if (selectedConversationId === conversationId) {
          if (updated.length > 0) {
            setSelectedConversationId(updated[0].id);
          } else {
            setSelectedConversationId(null);
            setShowChatPanel(false);
          }
        }

        return updated;
      });
      // Clear messages if the deleted conversation was selected
      if (selectedConversationId === conversationId) {
        setMessages([]);
      }
    } catch (err) {
      console.error("Error deleting conversation", err);
    }
  }

  return (
    <AdminChatContext.Provider
      value={{
        showChatPanel,
        setShowChatPanel,
        conversations,
        selectedConversationId,
        setSelectedConversationId,
        messages,
        sendMessage,
        createConversation,
        deleteConversation,
        isSending,
      }}
    >
      {children}
    </AdminChatContext.Provider>
  );
}

/* ---------- HOOK ---------- */

export function useAdminChat() {
  const ctx = useContext(AdminChatContext);
  if (!ctx) {
    throw new Error("useAdminChat must be used within an AdminChatProvider");
  }
  return ctx;
}
