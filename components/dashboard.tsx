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
  const totalRevenue = findKPI('total_revenue')
  const activeCustomers = findKPI('active_customers')
  const churnRate = findKPI('churn_rate')

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
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
          <p className="text-text-secondary">Welcome back! Here&apos;s your business intelligence snapshot.</p>
        </div>
        <button 
          onClick={loadDashboardData}
          disabled={loading}
          className="p-2 border rounded-lg hover:bg-muted transition-colors disabled:opacity-50"
          style={{ borderColor: 'var(--border)' }}
          title="Reload Dashboard"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="p-4 bg-danger/10 border border-danger/30 text-danger rounded-xl flex items-center justify-between">
          <p className="text-sm font-medium">{error}</p>
          <button 
            onClick={loadDashboardData}
            className="text-xs underline font-semibold hover:opacity-80"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* KPI Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Business Health Score"
          value={loading ? '-' : String(Math.max(15, 100 - riskScoreValue))}
          unit="%"
          trend={loading ? 0 : decisions.length > 3 ? -4 : 2}
          color="accent"
          icon={<Zap className="w-5 h-5" />}
        />
        <KPICard
          title="Active Decisions"
          value={loading ? '-' : String(decisions.length)}
          unit=" actions"
          trend={loading ? 0 : decisions.length}
          color="secondary"
          icon={<AlertCircle className="w-5 h-5" />}
        />
        <KPICard
          title="Avg Expected ROI"
          value={loading ? '-' : String(avgROI)}
          unit="%"
          trend={6.5}
          color="success"
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <KPICard
          title="Risk Exposure Score"
          value={loading ? '-' : String(riskScoreValue)}
          unit=" / 100"
          trend={loading ? 0 : criticalCount > 0 ? 5.2 : -1.8}
          color="warning"
          icon={<AlertCircle className="w-5 h-5" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart title="Revenue Overview" type="line" />
        <Chart title="Decision Impact" type="bar" />
      </div>

      {/* Today's Decisions & AI Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Decision Feed */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-2xl font-bold">Priority Actions</h2>
          {loading ? (
            Array.from({ length: 2 }).map((_, idx) => (
              <div key={idx} className="bg-card border border-border rounded-xl p-6 h-32 animate-pulse bg-muted/30"></div>
            ))
          ) : decisions.length > 0 ? (
            decisions.slice(0, 3).map((decision) => (
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
            <div className="p-8 text-center bg-card border border-border rounded-xl text-text-secondary">
              No priority actions flagged. System operational.
            </div>
          )}
        </div>

        {/* AI Recommendations Sidebar */}
        <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-accent animate-pulse" />
              <h3 className="text-lg font-bold">AI Strategic Actions</h3>
            </div>
            
            {loading ? (
              <div className="space-y-3 animate-pulse">
                <div className="h-12 bg-muted rounded"></div>
                <div className="h-12 bg-muted rounded"></div>
              </div>
            ) : summary && summary.recommended_actions?.length > 0 ? (
              <div className="space-y-3">
                {summary.recommended_actions.slice(0, 4).map((action, idx) => (
                  <div 
                    key={idx} 
                    className="p-3 bg-muted rounded-lg border border-border hover:border-accent transition-colors cursor-pointer"
                  >
                    <p className="text-sm font-medium">{action}</p>
                    <p className="text-xs text-text-secondary mt-1">Recommended AI Task</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 border border-dashed rounded-lg border-border">
                <p className="text-xs text-text-secondary">Upload data to receive AI recommendations.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Row 3: Business Health Summary & Recent Activity / Uploads */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Business Health Summary */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Business Health Summary</h3>
          {loading ? (
            <div className="h-20 bg-muted rounded animate-pulse"></div>
          ) : summary?.business_health_summary ? (
            <p className="text-sm leading-relaxed text-foreground bg-muted/40 p-4 rounded-lg border border-border">
              {summary.business_health_summary}
            </p>
          ) : (
            <div className="text-center py-8 border border-dashed border-border rounded-lg text-text-secondary">
              No business health metrics computed. Upload datasets to generate summaries.
            </div>
          )}
        </div>

        {/* Recent Activity / Uploads */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">Recent Uploads</h3>
          {loading ? (
            <div className="space-y-3">
              <div className="h-10 bg-muted rounded animate-pulse"></div>
              <div className="h-10 bg-muted rounded animate-pulse"></div>
            </div>
          ) : uploads.length > 0 ? (
            <div className="space-y-3">
              {uploads.slice(0, 3).map((up) => (
                <div key={up.upload_id} className="flex items-center gap-3 p-2 bg-muted/50 rounded-lg text-xs">
                  <FileText className="w-4 h-4 text-accent" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold truncate">{up.filename}</p>
                    <p className="text-text-secondary">{up.rows} rows × {up.columns} cols</p>
                  </div>
                  <span className="text-success font-bold">QS: {up.quality_score}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 border border-dashed rounded-lg border-border">
              <p className="text-xs text-text-secondary">No datasets uploaded yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
