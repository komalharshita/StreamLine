'use client'

import { useState } from 'react'
import Image from 'next/image'
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
          {/* Custom StreamLine Mask Logo */}
          <div className="relative w-8 h-8 flex-shrink-0">
            <Image 
              src="/logo.png" 
              alt="StreamLine Logo" 
              fill
              sizes="32px"
              priority
              className="object-contain rounded-md"
            />
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
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 relative group cursor-pointer ${
                isActive 
                  ? 'bg-white/[0.06] text-white font-medium' 
                  : 'text-muted-foreground hover:text-slate-100 hover:bg-white/[0.03]'
              }`}
            >
              {/* Active vertical line indicator */}
              {isActive && (
                <span className="absolute left-0 top-2.5 bottom-2.5 w-1 rounded-r-md bg-accent shadow-[0_0_8px_rgba(0,212,255,0.4)]" />
              )}
              
              <Icon className={`w-4 h-4 flex-shrink-0 transition-colors ${
                isActive ? 'text-accent' : 'text-muted-foreground group-hover:text-slate-200'
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
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 text-muted-foreground hover:text-slate-100 hover:bg-white/[0.03] group cursor-pointer"
            >
              <Icon className="w-4 h-4 flex-shrink-0 text-muted-foreground group-hover:text-slate-200" />
              {!collapsed && <span className="text-xs tracking-wide">{item.label}</span>}
            </button>
          )
        })}

        {/* Collapse Button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 text-muted-foreground/60 hover:text-slate-200 hover:bg-white/[0.03] mt-2 border-t border-border/50 pt-3 cursor-pointer"
        >
          <ChevronDown 
            className={`w-4 h-4 flex-shrink-0 transition-transform duration-200 text-muted-foreground/50 ${
              collapsed ? '-rotate-90' : 'rotate-90'
            }`} 
          />
          {!collapsed && <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/60">Collapse</span>}
        </button>
      </div>
    </div>
  )
}
