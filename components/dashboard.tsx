'use client'

import { TrendingUp, AlertCircle, Zap } from 'lucide-react'
import { KPICard } from './kpi-card'
import { DecisionCard } from './decision-card'
import { Chart } from './chart'

export function Dashboard() {
  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-text-secondary">Welcome back! Here&apos;s your business intelligence snapshot.</p>
      </div>

      {/* KPI Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Business Health Score"
          value="87"
          unit="%"
          trend={5}
          color="accent"
          icon={<Zap className="w-5 h-5" />}
        />
        <KPICard
          title="Decision Readiness"
          value="24"
          unit=" ready"
          trend={12}
          color="secondary"
          icon={<AlertCircle className="w-5 h-5" />}
        />
        <KPICard
          title="Avg ROI (Recommendations)"
          value="34.5"
          unit="%"
          trend={8.2}
          color="success"
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <KPICard
          title="Risk Score"
          value="12"
          unit=" / 100"
          trend={-2.1}
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
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-2xl font-bold">Today&apos;s Decision Feed</h2>
          <DecisionCard
            priority="high"
            title="Inventory Optimization"
            rootCause="Seasonal demand spike detected"
            impact="$125K potential savings"
            confidence={94}
            recommendation="Increase SKU allocation by 18%"
            expectedROI={42}
          />
          <DecisionCard
            priority="medium"
            title="Customer Churn Risk"
            rootCause="Reduced purchase frequency in segment A"
            impact="$89K at risk"
            confidence={78}
            recommendation="Launch targeted retention campaign"
            expectedROI={28}
          />
          <DecisionCard
            priority="low"
            title="Supply Chain Efficiency"
            rootCause="Route optimization opportunity"
            impact="$34K cost reduction"
            confidence={65}
            recommendation="Consolidate warehouse deliveries"
            expectedROI={18}
          />
        </div>

        {/* AI Recommendations Sidebar */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-bold mb-4">AI Recommendations</h3>
          <div className="space-y-3">
            <div className="p-3 bg-muted rounded-lg border border-border hover:border-accent transition-colors cursor-pointer">
              <p className="text-sm font-medium">Dynamic Pricing Strategy</p>
              <p className="text-xs text-text-secondary mt-1">Based on market volatility</p>
            </div>
            <div className="p-3 bg-muted rounded-lg border border-border hover:border-accent transition-colors cursor-pointer">
              <p className="text-sm font-medium">Staff Scheduling Optimization</p>
              <p className="text-xs text-text-secondary mt-1">18% efficiency gain possible</p>
            </div>
            <div className="p-3 bg-muted rounded-lg border border-border hover:border-accent transition-colors cursor-pointer">
              <p className="text-sm font-medium">Product Mix Rebalancing</p>
              <p className="text-xs text-text-secondary mt-1">Margin improvement identified</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="text-lg font-bold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between pb-3 border-b border-border last:border-b-0">
              <div>
                <p className="text-sm font-medium">Decision #{i} Resolved</p>
                <p className="text-xs text-text-secondary">2 hours ago</p>
              </div>
              <span className="text-xs px-2 py-1 bg-success/20 text-success rounded">Accepted</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
