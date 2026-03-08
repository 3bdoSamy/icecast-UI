'use client'

import Link from 'next/link'
import { ReactNode } from 'react'

const pages = [
  { label: 'Dashboard', href: '/' },
  { label: 'Sockets', href: '/sockets' },
  { label: 'Relays', href: '/relays' },
  { label: 'Listeners', href: '/listeners' },
  { label: 'Mount editor', href: '/mount-editor' },
  { label: 'Limits', href: '/limits' },
  { label: 'Paths', href: '/paths' },
  { label: 'Logging', href: '/logging' },
  { label: 'Security', href: '/security' }
]

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-[220px_1fr]">
      <aside className="border-r border-zinc-800 p-4">
        <h1 className="text-lg font-semibold mb-6">Icecast Control Center</h1>
        <nav className="space-y-2">
          {pages.map((page) => (
            <Link key={page.label} href={page.href} className="block text-sm text-zinc-300 hover:text-white">
              {page.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="p-6">{children}</main>
    </div>
  )
}
