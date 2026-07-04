'use client'

import { useState } from 'react'
import { Search, Filter } from 'lucide-react'
import { DecisionCard } from './decision-card'

export function DecisionFeed() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPriority, setSelectedPriority] = useState<'all' | 'high' | 'medium' | 'low'>('all')

  const decisions = [
    {
      priority: 'high',
      title: 'Inventory Optimization',
      rootCause: 'Seasonal demand spike detected',
      impact: '$125K potential savings',
      confidence: 94,
      recommendation: 'Increase SKU allocation by 18%',
      expectedROI: 42,
    },
    {
      priority: 'high',
      title: 'Price Elasticity Opportunity',
      rootCause: 'Market segment willingness to pay analysis',
      impact: '$89K revenue increase',
      confidence: 88,
      recommendation: 'Implement tiered pricing strategy',
      expectedROI: 35,
    },
    {
      priority: 'medium',
      title: 'Customer Churn Risk',
      rootCause: 'Reduced purchase frequency in segment A',
      impact: '$89K at risk',
      confidence: 78,
      recommendation: 'Launch targeted retention campaign',
      expectedROI: 28,
    },
    {
      priority: 'medium',
      title: 'Supply Chain Optimization',
      rootCause: 'Route inefficiency detected',
      impact: '$45K cost reduction',
      confidence: 72,
      recommendation: 'Consolidate warehouse network',
      expectedROI: 22,
    },
    {
      priority: 'low',
      title: 'Staff Scheduling Efficiency',
      rootCause: 'Demand forecasting variance analysis',
      impact: '$34K operational savings',
      confidence: 65,
      recommendation: 'Implement dynamic shift scheduling',
      expectedROI: 18,
    },
  ]

  const filtered = decisions.filter((d) => {
    const matchesSearch = d.title.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesPriority = selectedPriority === 'all' || d.priority === selectedPriority
    return matchesSearch && matchesPriority
  })

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Decision Feed</h1>
        <p className="text-text-secondary">AI-generated business decisions ranked by priority and potential impact.</p>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            placeholder="Search decisions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-card border border-border rounded-lg pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
          />
        </div>

        <div className="flex gap-2">
          {(['all', 'high', 'medium', 'low'] as const).map((priority) => (
            <button
              key={priority}
              onClick={() => setSelectedPriority(priority)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                selectedPriority === priority
                  ? 'bg-accent text-card'
                  : 'bg-card border border-border text-foreground hover:border-accent'
              }`}
            >
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Decisions List */}
      <div className="space-y-4">
        {filtered.length > 0 ? (
          filtered.map((decision, i) => (
            <DecisionCard
              key={i}
              priority={decision.priority as 'high' | 'medium' | 'low'}
              title={decision.title}
              rootCause={decision.rootCause}
              impact={decision.impact}
              confidence={decision.confidence}
              recommendation={decision.recommendation}
              expectedROI={decision.expectedROI}
            />
          ))
        ) : (
          <div className="text-center py-12 bg-card border border-border rounded-xl">
            <p className="text-text-secondary mb-2">No decisions found</p>
            <p className="text-sm text-text-secondary">Try adjusting your filters</p>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-text-secondary text-sm mb-2">Total Decisions</p>
          <p className="text-3xl font-bold">{decisions.length}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-text-secondary text-sm mb-2">Average Confidence</p>
          <p className="text-3xl font-bold">
            {Math.round(decisions.reduce((sum, d) => sum + d.confidence, 0) / decisions.length)}%
          </p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-text-secondary text-sm mb-2">Total Potential Value</p>
          <p className="text-3xl font-bold">$382K</p>
        </div>
      </div>
    </div>
  )
}
