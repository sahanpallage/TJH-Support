"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/admin/recent", label: "Recent" },
  { href: "/admin/dashboard", label: "Dashboard" },
  { href: "/admin/settings", label: "Settings" },
];

const customers = [
  "Annabelle Garcia",
  "John Doe",
  "Jane Smith",
  "Jim Beam",
  "Jill Johnson",
  "Peter Parker",
  "Tony Stark",
];

type Props = {
  collapsed: boolean;
};

export function AdminSidebar({ collapsed }: Props) {
  const pathname = usePathname();

  return (
    <aside
      className={`flex flex-col border-r border-slate-200 bg-white transition-all duration-200 ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      {/* Brand / logo area */}
      <div className="flex items-center gap-2 border-b border-slate-200 px-4 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-300 text-xs">
          TJH
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-sky-600">
            TJH Support
          </span>
        )}
      </div>

      {/* Section: navigation */}
      <div className="border-b border-slate-200 px-4 py-4">
        {!collapsed && (
          <div className="mb-2 text-xs font-semibold text-slate-500">
            TJH Job Application Support
          </div>
        )}

        <nav className="space-y-1 text-sm">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 ${
                  active
                    ? "bg-sky-500 text-white"
                    : "text-slate-700 hover:bg-slate-100"
                } ${collapsed ? "px-1 text-center" : ""}`}
              >
                {collapsed ? item.label[0] : item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Section: customer list */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {!collapsed && (
          <div className="mb-2 text-xs font-semibold text-slate-500">
            Customer List
          </div>
        )}
        <ul className="space-y-1 text-sm">
          {customers.map((c, index) => (
            <li key={c}>
              <button
                type="button"
                className={`w-full rounded-md text-left ${
                  collapsed ? "px-1 py-2 text-center" : "px-3 py-2"
                } ${
                  index === 0
                    ? "cursor-pointer bg-sky-500 text-white"
                    : "cursor-pointer text-slate-700 hover:bg-slate-100"
                }`}
              >
                {collapsed ? c.split(" ")[0][0] + c.split(" ")[1][0] : c}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
