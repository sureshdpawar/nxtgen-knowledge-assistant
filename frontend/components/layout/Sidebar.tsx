import {
  LayoutDashboard,
  Database,
  MessageSquare,
  Search,
  Settings,
} from "lucide-react";

const menu = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Knowledge Bases",
    icon: Database,
  },
  {
    label: "Conversations",
    icon: MessageSquare,
  },
  {
    label: "Search",
    icon: Search,
  },
  {
    label: "Settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r bg-slate-50">
      <nav className="space-y-2 p-4">
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition hover:bg-slate-200"
            >
              <Icon className="h-5 w-5" />

              {item.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}