"use client";

import type { ReactNode } from "react";
import { useState } from "react";
import { AdminSidebar } from "@/components/admin/Sidebar";
import { ChatPanel } from "@/components/admin/ChatPanel";
import { AdminChatProvider, useAdminChat } from "@/contexts/AdminChatContext";

function AdminLayoutContent({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [chatPanelWidth, setChatPanelWidth] = useState(320); // 320px = w-80
  const { showChatPanel, conversations, messages, selectedConversationId } =
    useAdminChat();

  return (
    <div className="flex h-screen w-full flex-col bg-slate-50 text-slate-900">
      {/* TOP HEADER – spans full width, no vertical seam */}
      <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
        <div className="flex items-center gap-4">
          {/* Hamburger toggles sidebar */}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-slate-300 hover:bg-slate-50"
          >
            <div className="space-y-1">
              <div className="h-[2px] w-4 bg-slate-700" />
              <div className="h-[2px] w-4 bg-slate-700" />
              <div className="h-[2px] w-4 bg-slate-700" />
            </div>
          </button>

          {/* Avatar + name */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-slate-200" />
            <div>
              <div className="text-sm font-semibold">Annabelle Garcia</div>
              <div className="text-xs text-slate-500">
                Chief of Staff, Business Operations Manager
              </div>
            </div>
          </div>
        </div>

        {/* JA Mem pill */}
        <button className="h-9 rounded-full border border-slate-300 px-5 text-xs font-medium">
          JA Mem
        </button>
      </header>

      {/* BELOW HEADER: sidebar + main + right panel */}
      <div className="flex flex-1 overflow-hidden">
        <AdminSidebar collapsed={collapsed} />

        <main className="flex-1 overflow-y-auto px-8 py-6">{children}</main>

        {showChatPanel && (
          <aside
            className="hidden border-l border-slate-200 bg-white xl:flex"
            style={{ width: `${chatPanelWidth}px` }}
          >
            <ChatPanel
              conversation={
                conversations.find((c) => c.id === selectedConversationId) ??
                null
              }
              messages={messages.filter(
                (m) => m.conversation_id === selectedConversationId,
              )}
              width={chatPanelWidth}
              onWidthChange={setChatPanelWidth}
            />
          </aside>
        )}
      </div>
    </div>
  );
}

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <AdminChatProvider>
      <AdminLayoutContent>{children}</AdminLayoutContent>
    </AdminChatProvider>
  );
}
