// src/app/admin/settings/page.tsx

"use client";

export default function CustomerSettingsPage() {
  const customerName = "Annabelle Garcia";

  return (
    <div className="max-w-5xl space-y-8">
      {/* Page title */}
      <div>
        <h1 className="text-xl font-semibold text-slate-900">
          Customer Settings – {customerName}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Edit profile information and preferences for this customer.
        </p>
      </div>

      {/* PROFILE SETTINGS */}
      <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800">
          Profile Settings
        </h2>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Full Name
            </label>
            <input
              type="text"
              defaultValue={customerName}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Email Address
            </label>
            <input
              type="email"
              defaultValue="annabelle.garcia@example.com"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Job Title
            </label>
            <input
              type="text"
              defaultValue="Chief of Staff"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Department
            </label>
            <input
              type="text"
              defaultValue="Operations"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div className="md:col-span-2">
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Location
            </label>
            <input
              type="text"
              defaultValue="New York, USA"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
          </div>
        </div>

        {/* avatar + actions */}
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 overflow-hidden rounded-full bg-slate-200" />
          <button className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50">
            Change Photo
          </button>
        </div>

        <div className="flex justify-end gap-2">
          <button className="rounded-md border border-slate-300 px-4 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50">
            Cancel
          </button>
          <button className="rounded-md bg-sky-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-sky-700">
            Save Changes
          </button>
        </div>
      </section>

      {/* NOTIFICATION PREFERENCES */}
      <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800">
          Notification Preferences
        </h2>

        {/* Email toggle */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-800">Enable Email Notifications</p>
            <p className="text-xs text-slate-500">
              Send this customer updates about their job search.
            </p>
          </div>

          {/* Simple toggle */}
          <label className="relative inline-flex cursor-pointer items-center">
            <input
              type="checkbox"
              defaultChecked
              className="peer sr-only"
            />
            <div className="peer h-6 w-11 rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500 peer-focus:outline-none" />
            <span className="absolute top-0.5 left-0.5 h-5 w-5 transform rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
          </label>
        </div>

        {/* Email categories */}
        <div className="space-y-2 text-sm text-slate-800">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              defaultChecked
              className="h-4 w-4"
            />
            <span>System Updates</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              defaultChecked
              className="h-4 w-4"
            />
            <span>Performance Review Reminders</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              className="h-4 w-4"
            />
            <span>Feedback Requests</span>
          </label>
        </div>

        {/* In-app alerts toggle */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-800">Show In-App Alerts</p>
            <p className="text-xs text-slate-500">
              Display notifications inside the JobProMax portal.
            </p>
          </div>
          <label className="relative inline-flex cursor-pointer items-center">
            <input
              type="checkbox"
              defaultChecked
              className="peer sr-only"
            />
            <div className="peer h-6 w-11 rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500 peer-focus:outline-none" />
            <span className="absolute top-0.5 left-0.5 h-5 w-5 transform rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
          </label>
        </div>

        <div className="flex justify-end gap-2">
          <button className="rounded-md border border-slate-300 px-4 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50">
            Discard
          </button>
          <button className="rounded-md bg-sky-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-sky-700">
            Update Preferences
          </button>
        </div>
      </section>

      {/* SECURITY */}
      <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800">Security</h2>

        <div className="flex items-center justify-between text-sm">
          <span>Two-Factor Authentication</span>
          <label className="relative inline-flex cursor-pointer items-center">
            <input
              type="checkbox"
              className="peer sr-only"
            />
            <div className="h-6 w-11 rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500" />
            <span className="absolute top-0.5 left-0.5 h-5 w-5 transform rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
          </label>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span>Password</span>
          <button className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium hover:bg-slate-50">
            Change Password
          </button>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span>Active Sessions</span>
          <button className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium hover:bg-slate-50">
            View Sessions
          </button>
        </div>
      </section>

      {/* PRIVACY CONTROLS */}
      <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800">
          Privacy Controls
        </h2>

        <div className="flex items-center justify-between text-sm">
          <div>
            <p>Allow recruiters to view full profile</p>
            <p className="text-xs text-slate-500">
              When enabled, matched recruiters can see this customer’s profile.
            </p>
          </div>
          <label className="relative inline-flex cursor-pointer items-center">
            <input
              type="checkbox"
              defaultChecked
              className="peer sr-only"
            />
            <div className="h-6 w-11 rounded-full bg-slate-200 transition-colors peer-checked:bg-sky-500" />
            <span className="absolute top-0.5 left-0.5 h-5 w-5 transform rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
          </label>
        </div>

        <div className="flex items-center justify-between text-sm">
          <div>
            <p>Request a copy of personal data</p>
            <p className="text-xs text-slate-500">
              Generate a report of all stored information for this customer.
            </p>
          </div>
          <button className="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium hover:bg-slate-50">
            Export Data
          </button>
        </div>
      </section>

      {/* LANGUAGE & REGION */}
      <section className="mb-4 space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-800">
          Language &amp; Region
        </h2>

        <div className="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Language
            </label>
            <select className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none">
              <option>English</option>
              <option>German</option>
              <option>French</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Timezone
            </label>
            <select className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 focus:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:outline-none">
              <option>Pacific Standard Time (PST)</option>
              <option>Eastern Standard Time (EST)</option>
              <option>Central European Time (CET)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <button className="rounded-md border border-slate-300 px-4 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50">
            Reset
          </button>
          <button className="rounded-md bg-sky-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-sky-700">
            Apply
          </button>
        </div>
      </section>
    </div>
  );
}
