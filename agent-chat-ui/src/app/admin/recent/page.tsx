const supportPortalUrl =
  process.env.NEXT_PUBLIC_SUPPORT_PORTAL_URL ?? undefined;

export default function AdminRecentPage() {
  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="mb-2 text-xl font-semibold">Recent Activity</h1>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-2 text-sm font-semibold text-slate-700">
          Recently Viewed Customers
        </h2>
        <ul className="space-y-1 text-sm text-slate-700">
          <li>Annabelle Garcia</li>
          <li>Varun Manny</li>
          <li>Emily Chen</li>
        </ul>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-2 text-sm font-semibold text-slate-700">
          Recent Documents
        </h2>
        <p className="text-sm text-slate-700">Resumes, 360 (Google Drive)</p>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-2 text-sm font-semibold text-slate-700">
          Recent Conversations
        </h2>
        <ul className="space-y-1 text-sm text-slate-700">
          <li>Chief of Staff Job Search</li>
          <li>Business Operations Job Search</li>
          <li>
            {supportPortalUrl ? (
              <a
                className="text-sky-600 hover:underline"
                href={supportPortalUrl}
                rel="noreferrer"
                target="_blank"
              >
                {supportPortalUrl.replace(/^https?:\/\//, "")}
              </a>
            ) : (
              "Support Portal"
            )}
          </li>
        </ul>
      </section>
    </div>
  );
}
