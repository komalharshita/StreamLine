'use client'

import { useState } from 'react'
import { Airplay, Shield, Cpu, Play, CheckCircle2, AlertCircle, Clock } from 'lucide-react'

interface RunRecord {
  id: string
  timestamp: string
  action: string
  triggerSource: 'Autopilot' | 'Manual Override'
  status: 'success' | 'pending_approval' | 'running'
  impact: string
}

export function DecisionPilot() {
  const [autopilotEnabled, setAutopilotEnabled] = useState(false)
  const [requireConfirmation, setRequireConfirmation] = useState(true)
  
  const [runs, setRuns] = useState<RunRecord[]>([
    {
      id: 'run-101',
      timestamp: '2026-07-05 16:12:10',
      action: 'Re-route Tokyo smartwatch warehouse inventory to Singapore',
      triggerSource: 'Manual Override',
      status: 'success',
      impact: '$18,500 savings'
    },
    {
      id: 'run-102',
      timestamp: '2026-07-05 17:01:45',
      action: 'Deploy Virginia earbud markdown promotion parameters',
      triggerSource: 'Autopilot',
      status: 'pending_approval',
      impact: '$8,200 savings'
    },
    {
      id: 'run-103',
      timestamp: '2026-07-05 17:20:00',
      action: 'Query active telemetry logs and notify account directors',
      triggerSource: 'Autopilot',
      status: 'running',
      impact: '$54,000 mitigation'
    }
  ])

  const handleApprove = (id: string) => {
    setRuns(prev => prev.map(r => r.id === id ? { ...r, status: 'success' } : r))
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="border-b border-border/40 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white font-sans flex items-center gap-2">
          <Airplay className="w-6 h-6 text-accent" />
          <span>DecisionPilot</span>
        </h1>
        <p className="text-xs text-muted-foreground mt-1">Autonomous policy execution control and deployment safety configuration.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Safety Lock Configurations */}
        <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-border/40 pb-3">
              <Shield className="w-4.5 h-4.5 text-accent" />
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Safety Controls</h3>
            </div>
            
            <p className="text-[11px] text-muted-foreground leading-relaxed">
              Configure validation locks to prevent autonomous pipelines from executing financial actions without direct human signature.
            </p>

            <div className="space-y-4 pt-2">
              {/* Autopilot Switch */}
              <div className="flex items-center justify-between gap-4 p-3 bg-background/50 border border-border/60 rounded-lg">
                <div className="space-y-0.5">
                  <p className="text-xs font-semibold text-slate-200">Autopilot Trigger</p>
                  <p className="text-[10px] text-muted-foreground">AI executes low-risk suggestions</p>
                </div>
                <button 
                  onClick={() => setAutopilotEnabled(!autopilotEnabled)}
                  className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${
                    autopilotEnabled ? 'bg-accent' : 'bg-muted border border-border'
                  }`}
                >
                  <span className={`absolute top-0.5 w-3.5 h-3.5 rounded-full bg-white transition-all ${
                    autopilotEnabled ? 'right-0.5' : 'left-0.5'
                  }`} />
                </button>
              </div>

              {/* Confirmation Switch */}
              <div className="flex items-center justify-between gap-4 p-3 bg-background/50 border border-border/60 rounded-lg">
                <div className="space-y-0.5">
                  <p className="text-xs font-semibold text-slate-200">Manual Confirmation</p>
                  <p className="text-[10px] text-muted-foreground">Always require sign-off for critical risk</p>
                </div>
                <button 
                  onClick={() => setRequireConfirmation(!requireConfirmation)}
                  className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${
                    requireConfirmation ? 'bg-accent' : 'bg-muted border border-border'
                  }`}
                >
                  <span className={`absolute top-0.5 w-3.5 h-3.5 rounded-full bg-white transition-all ${
                    requireConfirmation ? 'right-0.5' : 'left-0.5'
                  }`} />
                </button>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <div className="flex items-center gap-2 p-2.5 bg-accent/5 border border-accent/15 rounded-lg text-[10px] text-accent font-medium leading-normal">
              <Cpu className="w-4 h-4 flex-shrink-0 animate-pulse" />
              <span>Pilot is listening for dataset updates. Autopilot actions will queue below.</span>
            </div>
          </div>
        </div>

        {/* Execution Telemetry Log */}
        <div className="lg:col-span-2 bg-card/40 border border-border/80 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-border/40 pb-3">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Telemetry Run History</h3>
            <span className="text-[9px] uppercase tracking-wider font-bold text-accent bg-accent/10 px-2 py-0.5 rounded">Active Queue</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-border/40 text-muted-foreground text-[10px] uppercase font-bold tracking-wider">
                  <th className="py-2.5">Timestamp</th>
                  <th className="py-2.5">Action Plan</th>
                  <th className="py-2.5">Source</th>
                  <th className="py-2.5">Leverage</th>
                  <th className="py-2.5 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/20">
                {runs.map((run) => {
                  const getStatusBadge = (status: string) => {
                    if (status === 'success') {
                      return (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Success</span>
                        </span>
                      )
                    }
                    if (status === 'pending_approval') {
                      return (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                          <Clock className="w-3 h-3" />
                          <span>Needs Sign-off</span>
                        </span>
                      )
                    }
                    return (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-accent bg-accent/10 px-2 py-0.5 rounded-full border border-accent/20">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        <span>Running</span>
                      </span>
                    )
                  }

                  return (
                    <tr key={run.id} className="hover:bg-white/[0.01] transition-colors">
                      <td className="py-3 text-muted-foreground font-mono text-[10px]">{run.timestamp}</td>
                      <td className="py-3 font-medium text-slate-200 max-w-xs truncate">{run.action}</td>
                      <td className="py-3 text-muted-foreground">{run.triggerSource}</td>
                      <td className="py-3 font-semibold text-accent font-mono">{run.impact}</td>
                      <td className="py-3 text-right">
                        {run.status === 'pending_approval' ? (
                          <div className="flex justify-end gap-1.5">
                            <button 
                              onClick={() => handleApprove(run.id)}
                              className="px-2.5 py-1 bg-accent text-primary-foreground hover:bg-accent/90 shadow-[0_0_8px_rgba(0,212,255,0.25)] rounded text-[10px] font-bold cursor-pointer border border-accent/20"
                            >
                              Approve
                            </button>
                          </div>
                        ) : (
                          getStatusBadge(run.status)
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
