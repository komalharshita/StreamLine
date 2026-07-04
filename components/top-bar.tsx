'use client'

import { Search, Bell, Plus, ChevronDown } from 'lucide-react'

interface TopBarProps {
  onChatOpen: () => void
}

export function TopBar({ onChatOpen }: TopBarProps) {
  return (
    <div 
      className="px-8 py-4 flex items-center justify-between gap-4"
      style={{
        backgroundColor: 'var(--card)',
        borderBottom: '1px solid var(--border)',
        color: 'var(--foreground)'
      }}
    >
      {/* Left: Search */}
      <div className="flex-1 max-w-md relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
        <input
          type="text"
          placeholder="Search decisions, data, reports..."
          className="w-full border rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          style={{
            backgroundColor: 'var(--muted)',
            borderColor: 'var(--border)',
            color: 'var(--foreground)',
            '--tw-ring-color': 'var(--accent)'
          } as any}
        />
      </div>

      {/* Right: Workspace Selector, Notifications, Quick Upload, Profile */}
      <div className="flex items-center gap-3">
        {/* Workspace Selector */}
        <button 
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium hover:opacity-80"
          style={{ color: 'var(--foreground)' }}
        >
          <span>Workspace</span>
          <ChevronDown className="w-4 h-4" />
        </button>

        {/* Notifications */}
        <button className="relative p-2 rounded-lg transition-colors hover:opacity-80">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ backgroundColor: 'var(--danger)' }}></span>
        </button>

        {/* Quick Upload */}
        <button
          onClick={onChatOpen}
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium hover:opacity-90 transition-opacity text-sm"
          style={{
            backgroundColor: 'var(--accent)',
            color: 'var(--card)'
          }}
        >
          <Plus className="w-4 h-4" />
          Upload Data
        </button>

        {/* Profile */}
        <button className="flex items-center gap-2 w-10 h-10 rounded-lg transition-colors hover:opacity-80">
          <div 
            className="w-8 h-8 rounded-lg bg-gradient-to-br"
            style={{
              backgroundImage: 'linear-gradient(135deg, var(--accent), var(--secondary))'
            }}
          ></div>
        </button>
      </div>
    </div>
  )
}
