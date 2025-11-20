"use client";

import { useAdminChat, type Conversation } from "@/contexts/AdminChatContext";

export default function AdminDashboardPage() {
  const {
    conversations,
    selectedConversationId,
    setSelectedConversationId,
    setShowChatPanel,
    createConversation,
    deleteConversation,
  } = useAdminChat();

  async function handleAddConversation() {
    const defaultTitle = `Conversation ${conversations.length + 1}`;
    const input = window.prompt("Name this conversation:", defaultTitle);
    if (input === null) return;
    const sanitized = input.trim();
    await createConversation(sanitized || defaultTitle);
  }

  async function handleDeleteConversation(conv: Conversation) {
    const confirmed = window.confirm(
      `Delete "${conv.title}"? This cannot be undone.`,
    );
    if (!confirmed) return;
    await deleteConversation(conv.id);
  }

  return (
    <div className="max-w-4xl space-y-6">
      {/* Documents */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800">Documents</h2>
          <button className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50">
            + Add Document
          </button>
        </div>
        <div className="flex items-center justify-between rounded-md bg-slate-100 px-4 py-2 text-sm text-slate-800">
          <span>Resumes, 360 (Google Drive)</span>
          <span>🔗</span>
        </div>
        <p className="mt-3 text-xs text-slate-500">
          No additional documents found.
        </p>
      </section>

      {/* Conversations */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800">
            Conversations
          </h2>
          <button
            onClick={handleAddConversation}
            className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
          >
            + Add Conversation
          </button>
        </div>
        <ul className="space-y-1 text-sm">
          {conversations.map((conv) => {
            const active = conv.id === selectedConversationId;
            return (
              <li key={conv.id}>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedConversationId(conv.id);
                    setShowChatPanel(true);
                  }}
                  className={`w-full cursor-pointer rounded-md px-3 py-2 text-left ${
                    active
                      ? "bg-sky-100 font-medium text-sky-800"
                      : "text-slate-800 hover:bg-slate-100"
                  }`}
                >
                  {conv.title}
                  <span className="float-right flex items-center gap-2">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConversation(conv);
                      }}
                      className="cursor-pointer text-[11px] text-slate-500 underline-offset-2 hover:text-rose-600 hover:underline"
                    >
                      Delete
                    </button>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </section>

      {/* Jobs (for now simple bullets, you can swap to table later) */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800">Jobs</h2>
          <button className="inline-flex cursor-pointer items-center gap-2 rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50">
            + Add Job
          </button>
        </div>
        <ul className="list-inside list-disc space-y-1 text-sm text-slate-800">
          <li>Head of Product, SaaS (Interview Stage 3)</li>
          <li>Senior Marketing Manager (Offer Extended)</li>
          <li>Data Scientist (Application Reviewed)</li>
        </ul>
      </section>
    </div>
  );
}
