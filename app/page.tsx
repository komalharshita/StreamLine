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
            <div className="p-8 max-w-2xl">
              <h1 className="text-3xl font-bold mb-4">Analytics Reports</h1>
              <div className="border border-dashed border-border rounded-xl p-8 text-center bg-card space-y-4">
                <p className="text-text-secondary text-sm">No analytics reports have been generated yet.</p>
                <p className="text-xs text-text-secondary">
                  Please upload datasets on the Dashboard or Top Bar to trigger automated data cleaning, profiling, and intelligence reports.
                </p>
                <button 
                  onClick={() => setActiveTab('dashboard')}
                  className="px-4 py-2 bg-accent text-card text-xs font-semibold rounded-lg hover:opacity-90 transition-opacity"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* AI Chat Panel */}
      {chatOpen && <AIChat setIsOpen={setChatOpen} />}
    </div>
  )
}
