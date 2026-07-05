'use client'

import { useState } from 'react'
import { ChevronDown, CheckCircle, MessageCircle, DollarSign, Target } from 'lucide-react'

interface DecisionCardProps {
  priority: 'high' | 'medium' | 'low'
  title: string
  rootCause: string
  impact: string
  confidence: number
  recommendation: string
  expectedROI: number
}

const priorityStyles = {
  high: 'bg-rose-500/10 text-rose-400 border-rose-500/25',
  medium: 'bg-amber-500/10 text-amber-400 border-amber-500/25',
  low: 'bg-zinc-800 text-zinc-300 border-zinc-700/60',
}

const priorityLabel = {
  high: 'High Priority',
  medium: 'Medium Priority',
  low: 'Low Priority',
}

export function DecisionCard({
  priority,
  title,
  rootCause,
  impact,
  confidence,
  recommendation,
  expectedROI,
}: DecisionCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div 
      onClick={() => setExpanded(!expanded)}
      className={`bg-zinc-900/40 hover:bg-zinc-900/60 border border-border/80 hover:border-zinc-700 rounded-xl p-5 transition-all duration-200 cursor-pointer select-none group space-y-4 shadow-sm ${
        expanded ? 'bg-zinc-900/60 border-zinc-700' : ''
      }`}
    >
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${priorityStyles[priority]}`}>
                {priorityLabel[priority]}
              </span>
              <span className="text-[10px] text-zinc-500 font-semibold px-2 py-0.5 bg-zinc-900 border border-white/5 rounded-full">
                {confidence}% Confidence
              </span>
            </div>
            <h3 className="text-sm font-semibold text-zinc-200 group-hover:text-indigo-400 transition-colors duration-150 leading-snug">
              {title}
            </h3>
          </div>
          <button 
            type="button"
            className={`p-1 rounded-lg hover:bg-white/[0.04] text-zinc-500 hover:text-zinc-300 transition-all ${
              expanded ? 'rotate-180 text-zinc-300' : ''
            }`}
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>

        {/* Quick Preview Grid */}
        <div className="grid grid-cols-2 gap-4 pt-1 text-xs">
          <div className="space-y-1">
            <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider">Root Cause</p>
            <p className="font-medium text-zinc-300 truncate">{rootCause}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-wider">Financial Leverage</p>
            <p className="font-medium text-indigo-400 truncate">{impact}</p>
          </div>
        </div>

        {/* Expanded Accordion Panel */}
        {expanded && (
          <div 
            onClick={(e) => e.stopPropagation()} // Prevent accordion toggle when clicking inside
            className="space-y-4 pt-4 border-t border-border/60 animate-in fade-in slide-in-from-top-1 duration-200 cursor-default"
          >
            {/* Recommendation Document Box */}
            <div className="bg-indigo-650/[0.02] border border-indigo-500/15 rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-400">AI Recommendation</span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed font-medium">
                {recommendation}
              </p>
            </div>

            {/* Expected ROI Summary Cards */}
            <div className="grid grid-cols-2 gap-3.5">
              <div className="flex items-center gap-3 p-3 bg-zinc-900 border border-border/60 rounded-lg">
                <div className="w-8 h-8 rounded bg-zinc-800/80 flex items-center justify-center text-indigo-400 border border-white/5">
                  <Target className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Expected ROI</p>
                  <p className="text-sm font-bold text-indigo-400 font-mono">{expectedROI}%</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-3 bg-zinc-900 border border-border/60 rounded-lg">
                <div className="w-8 h-8 rounded bg-zinc-800/80 flex items-center justify-center text-emerald-400 border border-white/5">
                  <DollarSign className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Potential Gain</p>
                  <p className="text-sm font-bold text-emerald-400 font-mono">${(expectedROI * 5).toLocaleString()}K</p>
                </div>
              </div>
            </div>

            {/* Accordion Actions & Comments Footer */}
            <div className="flex items-center justify-between gap-4 pt-2">
              <div className="flex items-center gap-2 text-zinc-500 hover:text-zinc-300 transition-colors text-[10px] font-semibold cursor-pointer">
                <MessageCircle className="w-3.5 h-3.5" />
                <span>2 comments</span>
              </div>
              
              <div className="flex gap-2">
                <button 
                  type="button"
                  className="px-3 py-1.5 border border-border bg-zinc-900/60 hover:bg-zinc-900 hover:border-zinc-700 text-zinc-300 rounded-lg text-xs font-semibold transition-all duration-150"
                >
                  View Details
                </button>
                <button 
                  type="button"
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm hover:shadow-indigo-500/10 transition-all duration-150"
                >
                  Resolve
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
