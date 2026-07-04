'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { TopBar } from '@/components/top-bar'
import { Dashboard } from '@/components/dashboard'
import { DecisionFeed } from '@/components/decision-feed'
import { AIChat } from '@/components/ai-chat'

export default function Page() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <TopBar onChatOpen={() => setChatOpen(!chatOpen)} />

        {/* Content */}
        <main className="flex-1 overflow-auto">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'decision-feed' && <DecisionFeed />}
          {activeTab === 'analytics' && (
            <div className="p-8">
              <h1 className="text-3xl font-bold mb-4">Analytics</h1>
              <p className="text-text-secondary">Coming soon...</p>
            </div>
          )}
        </main>
      </div>

      {/* AI Chat Panel */}
      {chatOpen && <AIChat setIsOpen={setChatOpen} />}
    </div>
  )
}
