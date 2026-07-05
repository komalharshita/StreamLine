'use client'

import { useState, useEffect, useCallback } from 'react'
import { Search, Loader2, RefreshCw } from 'lucide-react'
import { DecisionCard } from './decision-card'
import { apiClient } from '@/lib/api-client'

interface Decision {
  decision_id: string
  priority_score: number
  priority_level: 'Critical' | 'High' | 'Medium' | 'Low'
  category: string
  title: string
  description: string
  root_cause: string
  financial_impact: number
  confidence_score: number
  recommendation: string
  expected_roi: number
  status: string
}

export function DecisionFeed() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPriority, setSelectedPriority] = useState<'all' | 'high' | 'medium' | 'low'>('all')
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDecisions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.get('/api/v1/decision-feed')
      setDecisions(data.decisions || [])
    } catch (err: any) {
      console.error('Failed to load decisions:', err)
      setError(err?.message || 'Failed to connect to decision feed service.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDecisions()

    // Listen for refresh triggers sent by TopBar uploads
    const handleRefresh = () => {
      fetchDecisions()
    }
    window.addEventListener('refresh-decisions', handleRefresh)
    return () => {
      window.removeEventListener('refresh-decisions', handleRefresh)
    }
  }, [fetchDecisions])

  const mapPriority = (p: string): 'high' | 'medium' | 'low' => {
    const pl = p.toLowerCase()
    if (pl === 'critical' || pl === 'high') return 'high'
    if (pl === 'medium') return 'medium'
    return 'low'
  }

  const formatImpact = (val: number): string => {
    if (val >= 1000) {
      return `$${(val / 1000).toFixed(0)}K potential savings`
    }
    return `$${val.toLocaleString()} potential savings`
  }

  const filtered = decisions.filter((d) => {
    const matchesSearch = d.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          d.root_cause.toLowerCase().includes(searchTerm.toLowerCase())
    const priorityMapped = mapPriority(d.priority_level)
    const matchesPriority = selectedPriority === 'all' || priorityMapped === selectedPriority
    return matchesSearch && matchesPriority
  })

  // Aggregates
  const totalDecisions = decisions.length
  const avgConfidence = totalDecisions > 0 
    ? Math.round(decisions.reduce((sum, d) => sum + d.confidence_score, 0) / totalDecisions)
    : 0
  const totalValue = decisions.reduce((sum, d) => sum + d.financial_impact, 0)
  const totalValueFormatted = totalValue >= 1000 
    ? `$${(totalValue / 1000).toFixed(0)}K` 
    : `$${totalValue.toLocaleString()}`

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold mb-2">Decision Feed</h1>
          <p className="text-text-secondary">AI-generated business decisions ranked by priority and potential impact.</p>
        </div>
        <button 
          onClick={fetchDecisions}
          disabled={loading}
          className="p-2 border rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
          style={{ borderColor: 'var(--border)' }}
          title="Refresh Feed"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
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
        {loading ? (
          // Skeleton Cards during loading state
          Array.from({ length: 3 }).map((_, i) => (
            <div 
              key={i} 
              className="bg-card border border-border rounded-xl p-6 space-y-4 animate-pulse"
            >
              <div className="flex justify-between items-center">
                <div className="h-6 w-28 bg-muted rounded"></div>
                <div className="h-4 w-20 bg-muted rounded"></div>
              </div>
              <div className="h-6 w-1/2 bg-muted rounded"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-10 bg-muted rounded"></div>
                <div className="h-10 bg-muted rounded"></div>
              </div>
            </div>
          ))
        ) : error ? (
          <div className="text-center py-12 bg-card border border-danger/20 rounded-xl text-danger space-y-3">
            <p className="font-semibold">{error}</p>
            <button 
              onClick={fetchDecisions}
              className="px-4 py-2 bg-accent text-card rounded-lg text-sm font-medium hover:opacity-90"
            >
              Retry Connection
            </button>
          </div>
        ) : filtered.length > 0 ? (
          filtered.map((decision) => (
            <DecisionCard
              key={decision.decision_id}
              priority={mapPriority(decision.priority_level)}
              title={decision.title}
              rootCause={decision.root_cause}
              impact={formatImpact(decision.financial_impact)}
              confidence={decision.confidence_score}
              recommendation={decision.recommendation}
              expectedROI={decision.expected_roi}
            />
          ))
        ) : (
          <div className="text-center py-12 bg-card border border-border rounded-xl">
            <p className="text-text-secondary mb-2">No decisions found</p>
            <p className="text-sm text-text-secondary">Ingest datasets or adjust your search filters to find active decisions.</p>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-text-secondary text-sm mb-2">Total Decisions</p>
          <p className="text-3xl font-bold">{loading ? '-' : totalDecisions}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-text-secondary text-sm mb-2">Average Confidence</p>
          <p className="text-3xl font-bold">{loading ? '-' : `${avgConfidence}%`}</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-6">
          <p className="text-text-secondary text-sm mb-2">Total Potential Value</p>
          <p className="text-3xl font-bold">{loading ? '-' : totalValueFormatted}</p>
        </div>
      </div>
    </div>
  )
}
