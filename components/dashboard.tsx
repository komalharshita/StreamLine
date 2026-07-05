'use client'

import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, AlertCircle, Zap, Loader2, RefreshCw, Sparkles, FileText, Database } from 'lucide-react'
import { KPICard } from './kpi-card'
import { DecisionCard } from './decision-card'
import { Chart } from './chart'
import { apiClient } from '@/lib/api-client'

interface KPIMetric {
  key: string
  label: string
  value: number
  change_percentage: number
  trend: 'up' | 'down'
}

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
  created_at: string
}

interface ExecutiveSummary {
  business_health_summary: string
  top_risks: string[]
  top_opportunities: string[]
  recommended_actions: string[]
}

interface UploadRecord {
  upload_id: string
  filename: string
  rows: number
  columns: number
  quality_score: number
  upload_time: string
}

export function Dashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [kpis, setKpis] = useState<KPIMetric[]>([])
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [uploads, setUploads] = useState<UploadRecord[]>([])
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.get('/api/v1/dashboard')
      if (data.system_status === 'error') {
        throw new Error(data.error || 'Server aggregation failed')
      }
      setDashboardData(data)
      setKpis(data.kpis || [])
      setDecisions(data.decisions || [])
      setUploads(data.recent_uploads || [])
      setSummary(data.executive_summary || null)
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err)
      setError(err?.message || 'Error communicating with analytics server.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDashboardData()

    const handleRefresh = () => {
      loadDashboardData()
    }
    window.addEventListener('refresh-decisions', handleRefresh)
    return () => {
      window.removeEventListener('refresh-decisions', handleRefresh)
    }
  }, [loadDashboardData])

  // Extract KPI card data
  const findKPI = (key: string) => kpis.find(k => k.key === key)
  
  // Calculate dynamic stats from decision list
  const criticalCount = decisions.filter(d => d.priority_level === 'Critical').length
  const highCount = decisions.filter(d => d.priority_level === 'High').length
  const avgROI = decisions.length > 0
    ? Math.round(decisions.reduce((sum, d) => sum + d.expected_roi, 0) / decisions.length)
    : 34.5
  const riskScoreValue = Math.min(100, criticalCount * 25 + highCount * 12 + decisions.length * 3)

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

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header Section */}
      <div className="flex justify-between items-center border-b border-border/40 pb-5">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-white font-sans">Dashboard</h1>
          <p className="text-xs text-muted-foreground">Welcome back! Here's your workspace telemetry and intelligence snapshot.</p>
        </div>
        <button 
          onClick={loadDashboardData}
          disabled={loading}
          className="p-2 border border-accent/20 hover:border-accent bg-accent/5 hover:bg-accent/15 text-accent rounded-lg transition-all duration-150 disabled:opacity-50 cursor-pointer shadow-[0_0_8px_rgba(0,212,255,0.1)]"
          title="Reload Dashboard"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="p-3.5 bg-rose-500/5 border border-rose-500/10 text-rose-400 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-top-2">
          <p className="text-xs font-semibold flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </p>
          <button 
            onClick={loadDashboardData}
            className="text-[10px] uppercase font-bold tracking-wider hover:underline text-rose-300 cursor-pointer"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* KPI Blocks */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Business Health Score"
          value={loading ? '-' : String(Math.max(15, 100 - riskScoreValue))}
          unit="%"
          trend={loading ? 0 : decisions.length > 3 ? -4 : 2}
          color="accent"
          icon={<Zap className="w-4.5 h-4.5" />}
        />
        <KPICard
          title="Active Decisions"
          value={loading ? '-' : String(decisions.length)}
          unit=" actions"
          trend={loading ? 0 : decisions.length}
          color="secondary"
          icon={<AlertCircle className="w-4.5 h-4.5" />}
        />
        <KPICard
          title="Avg Expected ROI"
          value={loading ? '-' : String(avgROI)}
          unit="%"
          trend={6.5}
          color="success"
          icon={<TrendingUp className="w-4.5 h-4.5" />}
        />
        <KPICard
          title="Risk Exposure Score"
          value={loading ? '-' : String(riskScoreValue)}
          unit=" / 100"
          trend={loading ? 0 : criticalCount > 0 ? 5.2 : -1.8}
          color="warning"
          icon={<AlertCircle className="w-4.5 h-4.5" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Chart title="Revenue Performance" type="line" />
        <Chart title="Decision Leverage & Impact" type="bar" />
      </div>

      {/* Priority Actions & AI Strategic recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Live Decision Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-sm font-semibold tracking-tight text-white">Priority Actions</h2>
            <span className="text-[10px] text-muted-foreground/80 font-medium">Ranked by Priority Score</span>
          </div>
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 2 }).map((_, idx) => (
                <div key={idx} className="bg-card/40 border border-border/80 rounded-xl p-6 h-28 animate-pulse"></div>
              ))}
            </div>
          ) : decisions.length > 0 ? (
            <div className="space-y-3">
              {decisions.slice(0, 3).map((decision) => (
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
              ))}
            </div>
          ) : (
            <div className="p-10 text-center bg-card/10 border border-dashed border-border rounded-xl text-muted-foreground/80 text-xs">
              No priority actions flagged. System operational.
            </div>
          )}
        </div>

        {/* AI Recommendations Sidebar */}
        <div className="bg-gradient-to-b from-card/60 via-card/20 to-secondary/5 border border-border/80 rounded-xl p-5 flex flex-col space-y-4">
          <div className="flex items-center gap-2 border-b border-border/40 pb-3">
            <Sparkles className="w-4 h-4 text-accent animate-pulse" />
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider">AI Strategic Actions</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="space-y-3">
                <div className="h-14 bg-card/60 rounded-lg animate-pulse"></div>
                <div className="h-14 bg-card/60 rounded-lg animate-pulse"></div>
              </div>
            ) : summary && summary.recommended_actions?.length > 0 ? (
              <div className="space-y-2.5">
                {summary.recommended_actions.slice(0, 4).map((action, idx) => (
                  <div 
                    key={idx} 
                    className="p-3 bg-card/40 border border-border/60 hover:border-accent/40 hover:bg-card/85 rounded-lg transition-all duration-150 cursor-pointer group"
                  >
                    <p className="text-xs text-slate-300 group-hover:text-white leading-normal font-medium">{action}</p>
                    <div className="flex items-center gap-1.5 mt-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse animate-duration-1000"></div>
                      <span className="text-[9px] uppercase tracking-wider font-bold text-muted-foreground/75 group-hover:text-accent transition-colors">Recommended Pilot Task</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 border border-dashed rounded-lg border-border/60 flex flex-col items-center justify-center space-y-2">
                <Sparkles className="w-5 h-5 text-muted-foreground/60" />
                <p className="text-[10px] text-muted-foreground/80 max-w-[180px] leading-relaxed">Upload business data to receive AI recommendations.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Health Summary & Recent Upload Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Business Health Summary Document */}
        <div className="lg:col-span-2 bg-card/40 border border-border/80 rounded-xl p-6 space-y-4">
          <div className="border-b border-border/40 pb-3 flex items-center justify-between">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Business Health Summary</h3>
            <span className="text-[9px] uppercase tracking-wider font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/15">AI Aggregated</span>
          </div>
          {loading ? (
            <div className="space-y-2.5">
              <div className="h-4 bg-card/60 rounded w-full animate-pulse"></div>
              <div className="h-4 bg-card/60 rounded w-5/6 animate-pulse"></div>
            </div>
          ) : summary?.business_health_summary ? (
            <div className="relative pl-4 border-l-2 border-accent bg-card/30 p-4 rounded-r-lg border border-border/40 border-l-0">
              <p className="text-xs leading-relaxed text-slate-300 font-medium">
                {summary.business_health_summary}
              </p>
            </div>
          ) : (
            <div className="text-center py-10 border border-dashed border-border/80 rounded-lg text-muted-foreground/80 text-xs">
              No business health metrics computed. Upload datasets to generate summaries.
            </div>
          )}
        </div>

        {/* Recent Activity Logs */}
        <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-4">
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider border-b border-border/40 pb-3">Recent Upload Logs</h3>
          
          {loading ? (
            <div className="space-y-3">
              <div className="h-12 bg-card/60 rounded-lg animate-pulse"></div>
              <div className="h-12 bg-card/60 rounded-lg animate-pulse"></div>
            </div>
          ) : uploads.length > 0 ? (
            <div className="space-y-2.5">
              {uploads.slice(0, 3).map((up) => {
                const getQualityBadgeColor = (score: number) => {
                  if (score >= 80) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  if (score >= 60) return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  return 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }
                return (
                  <div key={up.upload_id} className="flex items-center gap-3 p-3 bg-card/50 hover:bg-card/80 border border-border/60 rounded-lg transition-colors text-xs">
                    <div className="w-8 h-8 rounded-md bg-card border border-white/5 flex items-center justify-center text-slate-400 flex-shrink-0">
                      <FileText className="w-4 h-4 text-accent" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-slate-200 truncate">{up.filename}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{up.rows.toLocaleString()} rows × {up.columns} columns</p>
                    </div>
                    <div className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getQualityBadgeColor(up.quality_score)}`}>
                      QS: {up.quality_score}
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 border border-dashed rounded-lg border-border/80 flex flex-col items-center justify-center space-y-2">
              <Database className="w-5 h-5 text-muted-foreground/60" />
              <p className="text-[10px] text-muted-foreground/80">No datasets uploaded yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
