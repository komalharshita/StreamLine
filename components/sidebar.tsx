'use client'

import { useState } from 'react'
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
      className={`relative transition-all duration-300 ease-in-out flex flex-col h-screen select-none ${
        collapsed ? 'w-[72px]' : 'w-64'
      } bg-background border-r border-border`}
    >
      {/* Brand Logo Header */}
      <div 
        className="h-16 flex items-center px-4 border-b border-border"
      >
        <div className="flex items-center gap-3 ml-1">
          {/* Custom Premium Geometric Logo Symbol */}
          <div 
            className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-base transition-all duration-300 relative overflow-hidden shadow-sm group border border-white/10"
            style={{
              background: 'linear-gradient(135deg, var(--accent), #4f46e5)',
              color: '#ffffff'
            }}
          >
            <span className="relative z-10 font-mono tracking-tighter">S</span>
            <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          {!collapsed && (
            <span className="font-semibold text-sm tracking-tight text-white font-sans">
              StreamLine
            </span>
          )}
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 relative group ${
                isActive 
                  ? 'bg-white/[0.06] text-white font-medium' 
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.03]'
              }`}
            >
              {/* Active vertical line indicator */}
              {isActive && (
                <span className="absolute left-0 top-2.5 bottom-2.5 w-1 rounded-r-md bg-accent" />
              )}
              
              <Icon className={`w-4 h-4 flex-shrink-0 transition-colors ${
                isActive ? 'text-accent' : 'text-zinc-400 group-hover:text-zinc-200'
              }`} />
              
              {!collapsed && (
                <span className="text-xs tracking-wide">{item.label}</span>
              )}
            </button>
          )
        })}
      </nav>

      {/* Settings, Profile & Toggle Collapse */}
      <div 
        className="px-3 py-4 border-t border-border space-y-1 bg-background"
      >
        {bottomItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.03] group"
            >
              <Icon className="w-4 h-4 flex-shrink-0 text-zinc-400 group-hover:text-zinc-200" />
              {!collapsed && <span className="text-xs tracking-wide">{item.label}</span>}
            </button>
          )
        })}

        {/* Collapse Button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.03] mt-2 border-t border-border/50 pt-3"
        >
          <ChevronDown 
            className={`w-4 h-4 flex-shrink-0 transition-transform duration-200 ${
              collapsed ? '-rotate-90' : 'rotate-90'
            }`} 
          />
          {!collapsed && <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">Collapse</span>}
        </button>
      </div>
    </div>
  )
}
