'use client'

import Link from 'next/link'
import { BarChart3 } from 'lucide-react'

export default function AnalyticsRoute() {
  return (
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
        <Link 
          href="/dashboard"
          className="px-3.5 py-1.5 bg-[#18181b] hover:bg-[#27272a] text-white text-xs font-semibold rounded-lg transition-all duration-150 shadow-sm border border-border cursor-pointer"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  )
}
