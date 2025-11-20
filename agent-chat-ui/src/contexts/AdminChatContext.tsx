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
const MESSAGES_STORAGE_KEY = "adminChat.messages";

/* ---------- TYPES ---------- */

export type Conversation = {
  id: number;
  customer_id: number;
  title: string;
  external_thread_id: string;
  created_at: string;
};

export type Message = {
  id: string;
  conversationId: number;
  author: "agent" | "admin";
  text: string;
  createdAt: string;
};

type AdminChatContextType = {
  showChatPanel: boolean;
  setShowChatPanel: (show: boolean) => void;

  conversations: Conversation[];
  selectedConversationId: number | null;
  setSelectedConversationId: (id: number | null) => void;

  messages: Message[]; // all messages, filtered per conversation where needed
  sendMessage: (conversationId: number, text: string) => Promise<void>;
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

  // hydrate chat history from localStorage (per browser)
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(MESSAGES_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Message[];
        setMessages(parsed);
      }
    } catch (err) {
      console.warn("Failed to parse stored messages", err);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

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
        }
      } catch (err) {
        console.error("Failed to bootstrap admin chat context", err);
      }
    }

    bootstrap();
  }, []);

  // -------- sendMessage: frontend → FastAPI → JobProMax agent --------
  async function sendMessage(conversationId: number, text: string) {
    if (!text.trim()) return;

    const now = new Date().toISOString();
    const adminMessage: Message = {
      id: crypto.randomUUID(),
      conversationId,
      author: "admin",
      text,
      createdAt: now,
    };

    // Optimistic append of admin message
    setMessages((prev) => [...prev, adminMessage]);

    setIsSending(true);
    try {
      const res = await fetch(
        `${API_BASE}/chat/conversations/${conversationId}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        },
      );

      if (!res.ok) {
        console.error(
          "Failed to send chat message",
          res.status,
          await res.text(),
        );
        return;
      }

      const data = await res.json();
      const replyText: string =
        data.reply || data.message || data.content || "(no reply)";

      const agentMessage: Message = {
        id: crypto.randomUUID(),
        conversationId,
        author: "agent",
        text: replyText,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
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
      setMessages((prev) =>
        prev.filter((message) => message.conversationId !== conversationId),
      );
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
