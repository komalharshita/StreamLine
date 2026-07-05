'use client'

import { useState, useEffect, useCallback } from 'react'
import { Search, Loader2, RefreshCw, AlertCircle, TrendingUp } from 'lucide-react'
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
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-border/40 pb-5">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-white font-sans">Decision Feed</h1>
          <p className="text-xs text-zinc-400">AI-generated business insights and operations ranked by priority and financial leverage.</p>
        </div>
        <button 
          onClick={fetchDecisions}
          disabled={loading}
          className="p-2 border border-border bg-zinc-900/60 hover:bg-zinc-900 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200 rounded-lg transition-all duration-150 disabled:opacity-50 active:bg-zinc-800"
          title="Refresh Feed"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Search & Segment Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center">
        {/* Search Input */}
        <div className="flex-1 relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-indigo-400 transition-colors" />
          <input
            type="text"
            placeholder="Search decisions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-900/60 hover:bg-zinc-900 border border-border focus:border-accent/40 rounded-lg pl-9 pr-4 py-2.5 text-xs text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all duration-150"
          />
        </div>

        {/* Vercel-style Segment Selector */}
        <div className="bg-zinc-900 border border-border/80 rounded-lg p-1 flex gap-1">
          {(['all', 'high', 'medium', 'low'] as const).map((priority) => {
            const isActive = selectedPriority === priority
            return (
              <button
                key={priority}
                onClick={() => setSelectedPriority(priority)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold tracking-wide transition-all duration-150 capitalize ${
                  isActive
                    ? 'bg-zinc-800 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02]'
                }`}
              >
                {priority}
              </button>
            )
          })}
        </div>
      </div>

      {/* Decisions List */}
      <div className="space-y-3.5">
        {loading ? (
          // Skeleton Cards during loading state
          Array.from({ length: 3 }).map((_, i) => (
            <div 
              key={i} 
              className="bg-zinc-900/40 border border-border/80 rounded-xl p-6 space-y-4 animate-pulse"
            >
              <div className="flex justify-between items-center">
                <div className="h-5 w-24 bg-zinc-800 rounded"></div>
                <div className="h-4 w-16 bg-zinc-800 rounded"></div>
              </div>
              <div className="h-5 w-1/3 bg-zinc-800 rounded"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-9 bg-zinc-800 rounded"></div>
                <div className="h-9 bg-zinc-800 rounded"></div>
              </div>
            </div>
          ))
        ) : error ? (
          <div className="text-center py-12 bg-zinc-900/20 border border-rose-500/10 rounded-xl text-rose-400 space-y-4 max-w-xl mx-auto flex flex-col items-center justify-center p-6">
            <div className="w-10 h-10 rounded-lg bg-zinc-900 border border-white/5 flex items-center justify-center text-rose-400">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <p className="font-semibold text-xs text-zinc-200">Ingestion Inaccessible</p>
              <p className="text-[11px] text-zinc-500 max-w-xs leading-normal">{error}</p>
            </div>
            <button 
              onClick={fetchDecisions}
              className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-all duration-150 shadow-sm border border-indigo-500/10"
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
          <div className="text-center py-16 bg-zinc-900/10 border border-dashed border-border rounded-xl flex flex-col items-center justify-center space-y-3">
            <AlertCircle className="w-6 h-6 text-zinc-600" />
            <div className="space-y-1">
              <p className="text-xs font-semibold text-zinc-300">No decisions found</p>
              <p className="text-[11px] text-zinc-500 max-w-xs leading-relaxed">Ingest corporate datasets or adjust search filters to identify active business vectors.</p>
            </div>
          </div>
        )}
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-border/40">
        <div className="bg-zinc-900/40 border border-border/80 rounded-xl p-4.5 space-y-1.5">
          <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Total Decisions</p>
          <p className="text-2xl font-bold tracking-tight text-white">{loading ? '-' : totalDecisions}</p>
        </div>
        <div className="bg-zinc-900/40 border border-border/80 rounded-xl p-4.5 space-y-1.5">
          <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Average Confidence</p>
          <p className="text-2xl font-bold tracking-tight text-white">{loading ? '-' : `${avgConfidence}%`}</p>
        </div>
        <div className="bg-zinc-900/40 border border-border/80 rounded-xl p-4.5 space-y-1.5">
          <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Total Potential Value</p>
          <p className="text-2xl font-bold tracking-tight text-white">{loading ? '-' : totalValueFormatted}</p>
        </div>
      </div>
    </div>
  )
}
