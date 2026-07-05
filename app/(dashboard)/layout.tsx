'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { TopBar } from '@/components/top-bar'
import { AIChat } from '@/components/ai-chat'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-[#09090b] text-foreground antialiased font-sans">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar Header */}
        <TopBar onChatOpen={() => setChatOpen(!chatOpen)} />

        {/* Dynamic Route Content */}
        <main className="flex-1 overflow-y-auto bg-background/10">
          <div className="animate-in fade-in duration-200 ease-out">
            {children}
          </div>
        </main>
      </div>

      {/* Contextual AI Chat Panel Drawer */}
      {chatOpen && <AIChat setIsOpen={setChatOpen} />}
    </div>
  )
}
