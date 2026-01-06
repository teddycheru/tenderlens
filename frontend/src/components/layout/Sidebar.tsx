'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FileText, Sparkles, Bell, BarChart3, Settings } from 'lucide-react'

const menuItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'All Tenders',
    href: '/tenders',
    icon: FileText,
  },
  {
    name: 'AI Recommendations',
    href: '/recommendations',
    icon: Sparkles,
  },
  {
    name: 'Alerts',
    href: '/alerts',
    icon: Bell,
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-gray-900 text-white p-4 flex flex-col">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">TenderLens</h1>
        <p className="text-sm text-gray-400">Tender Management</p>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      <div className="pt-4 border-t border-gray-700 text-sm text-gray-400">
        <p>TenderLens MVP v1.0</p>
      </div>
    </aside>
  )
}
