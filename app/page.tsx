'use client'

import { useState } from 'react'
import { Sidebar } from '@/components/sidebar'
import { TopBar } from '@/components/top-bar'
import { Dashboard } from '@/components/dashboard'
import { DecisionFeed } from '@/components/decision-feed'
import { DecisionPilot } from '@/components/decision-pilot'
import { SimulationLab } from '@/components/simulation-lab'
import { Reports } from '@/components/reports'
import { DataCenter } from '@/components/data-center'
import { AIChat } from '@/components/ai-chat'
import { BarChart3 } from 'lucide-react'

export default function Page() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground antialiased font-sans">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <TopBar onChatOpen={() => setChatOpen(!chatOpen)} />

        {/* Content */}
        <main className="flex-1 overflow-y-auto bg-background/20">
          <div className="animate-in fade-in duration-200 ease-out">
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'decision-feed' && <DecisionFeed />}
            {activeTab === 'pilot' && <DecisionPilot />}
            {activeTab === 'simulation' && <SimulationLab />}
            {activeTab === 'reports' && <Reports />}
            {activeTab === 'data' && <DataCenter />}
            {activeTab === 'analytics' && (
              <div className="p-8 max-w-4xl mx-auto space-y-6">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-white mb-1">Analytics Reports</h1>
                  <p className="text-xs text-muted-foreground">View deep statistical analytics and telemetry details.</p>
                </div>
                
                {/* Premium Empty State */}
                <div className="border border-dashed border-border/80 rounded-xl p-12 text-center bg-card/20 backdrop-blur-xs flex flex-col items-center justify-center space-y-4 max-w-xl mx-auto mt-8">
                  <div className="w-10 h-10 rounded-lg bg-card border border-white/5 flex items-center justify-center text-muted-foreground shadow-sm">
                    <BarChart3 className="w-5 h-5 text-accent" />
                  </div>
                  <div className="space-y-1.5 max-w-md">
                    <p className="text-slate-200 text-xs font-semibold">No analytics reports generated</p>
                    <p className="text-[11px] text-muted-foreground/85 leading-relaxed">
                      Upload datasets on the Dashboard or Top Bar. StreamLine's automated data pipeline will clean, profile, and construct telemetry charts for your workspace.
                    </p>
                  </div>
                  <button 
                    onClick={() => setActiveTab('dashboard')}
                    className="px-3.5 py-1.5 bg-secondary hover:bg-secondary/90 text-white text-xs font-semibold rounded-lg transition-all duration-150 shadow-sm hover:shadow-secondary/15 border border-secondary/15 cursor-pointer"
                  >
                    Go to Dashboard
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* AI Chat Panel */}
      {chatOpen && <AIChat setIsOpen={setChatOpen} />}
    </div>
  )
}
