'use client'

import { useState } from 'react'
import { ChevronDown, CheckCircle, AlertCircle, MessageCircle } from 'lucide-react'

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
  high: 'bg-danger/20 text-danger border-danger/30',
  medium: 'bg-warning/20 text-warning border-warning/30',
  low: 'bg-secondary/20 text-secondary border-secondary/30',
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
    <div className="bg-card border border-border rounded-xl p-6 hover:border-accent transition-all cursor-pointer group">
      <div onClick={() => setExpanded(!expanded)} className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className={`text-xs font-bold px-3 py-1 rounded-lg border ${priorityStyles[priority]}`}>
                {priorityLabel[priority]}
              </span>
              <span className="text-xs text-text-secondary">{confidence}% Confidence</span>
            </div>
            <h3 className="text-lg font-bold group-hover:text-accent transition-colors">{title}</h3>
          </div>
          <button className={`transition-transform ${expanded ? 'rotate-180' : ''}`}>
            <ChevronDown className="w-5 h-5 text-text-secondary" />
          </button>
        </div>

        {/* Quick Preview */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-text-secondary text-xs mb-1">Root Cause</p>
            <p className="font-medium">{rootCause}</p>
          </div>
          <div>
            <p className="text-text-secondary text-xs mb-1">Financial Impact</p>
            <p className="font-medium text-accent">{impact}</p>
          </div>
        </div>

        {/* Expanded Content */}
        {expanded && (
          <div className="space-y-4 pt-4 border-t border-border">
            {/* Recommendation */}
            <div className="bg-secondary/10 border border-secondary/30 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-secondary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-text-secondary mb-1">AI Recommendation</p>
                  <p className="text-sm font-medium">{recommendation}</p>
                </div>
              </div>
            </div>

            {/* Expected ROI */}
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div>
                <p className="text-xs text-text-secondary">Expected ROI</p>
                <p className="text-2xl font-bold text-accent">{expectedROI}%</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-text-secondary">Potential Gain</p>
                <p className="text-lg font-bold">${expectedROI * 5}K</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button className="flex-1 bg-accent text-card px-4 py-2 rounded-lg font-medium hover:opacity-90 transition-opacity text-sm">
                Resolve
              </button>
              <button className="flex-1 border border-border px-4 py-2 rounded-lg font-medium hover:bg-muted transition-colors text-sm">
                View Details
              </button>
            </div>

            {/* Chat Section */}
            <div className="flex items-center gap-2 text-sm text-text-secondary hover:text-foreground transition-colors">
              <MessageCircle className="w-4 h-4" />
              <span>2 comments</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
