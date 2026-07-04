'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  LayoutDashboard,
  Zap,
  BarChart3,
  Beaker,
  Airplay,
  FileText,
  Database,
  Bell,
  Settings,
  User,
  ChevronDown,
  Logo,
} from 'lucide-react'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'decision-feed', label: 'Decision Feed', icon: Zap },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'simulation', label: 'Simulation Lab', icon: Beaker },
    { id: 'pilot', label: 'DecisionPilot', icon: Airplay },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'data', label: 'Data Center', icon: Database },
  ]

  const bottomItems = [
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'profile', label: 'Profile', icon: User },
  ]

  return (
    <div 
      className={`transition-all duration-300 flex flex-col ${collapsed ? 'w-20' : 'w-64'}`}
      style={{ 
        backgroundColor: 'var(--card)',
        borderRight: '1px solid var(--border)',
        color: 'var(--foreground)'
      }}
    >
      {/* Logo */}
      <div 
        className="p-6 flex items-center gap-3"
        style={{ 
          borderBottom: '1px solid var(--border)'
        }}
      >
        <div 
          className="w-10 h-10 bg-gradient-to-br rounded-lg flex items-center justify-center font-bold text-sm"
          style={{
            backgroundImage: 'linear-gradient(135deg, var(--accent), var(--secondary))',
            color: 'var(--card)'
          }}
        >
          S
        </div>
        {!collapsed && <span className="font-bold text-lg">StreamLine</span>}
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2 overflow-auto">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === item.id
                  ? 'font-semibold'
                  : 'hover:opacity-80'
              }`}
              style={{
                backgroundColor: activeTab === item.id ? 'var(--accent)' : 'transparent',
                color: activeTab === item.id ? 'var(--card)' : 'var(--text-secondary)'
              }}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="text-sm">{item.label}</span>}
            </button>
          )
        })}
      </nav>

      {/* Bottom Menu */}
      <div 
        className="p-4 space-y-2"
        style={{ 
          borderTop: '1px solid var(--border)'
        }}
      >
        {bottomItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all hover:opacity-80"
              style={{
                color: 'var(--text-secondary)'
              }}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="text-sm">{item.label}</span>}
            </button>
          )
        })}

        {/* Toggle Collapse */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all mt-4 hover:opacity-80"
          style={{
            color: 'var(--text-secondary)'
          }}
        >
          <ChevronDown className={`w-5 h-5 flex-shrink-0 transition-transform ${collapsed ? 'rotate-180' : ''}`} />
          {!collapsed && <span className="text-sm text-xs">Collapse</span>}
        </button>
      </div>
    </div>
  )
}
