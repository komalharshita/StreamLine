'use client'

import { TrendingUp, TrendingDown } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string
  unit: string
  trend: number
  color: 'accent' | 'secondary' | 'success' | 'warning'
  icon: React.ReactNode
}

const colorClasses = {
  accent: 'from-accent/20 to-accent/5 border-accent/30',
  secondary: 'from-secondary/20 to-secondary/5 border-secondary/30',
  success: 'from-success/20 to-success/5 border-success/30',
  warning: 'from-warning/20 to-warning/5 border-warning/30',
}

const textColorClasses = {
  accent: 'text-accent',
  secondary: 'text-secondary',
  success: 'text-success',
  warning: 'text-warning',
}

export function KPICard({ title, value, unit, trend, color, icon }: KPICardProps) {
  const isPositive = trend > 0
  const TrendIcon = isPositive ? TrendingUp : TrendingDown

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-xl p-6 backdrop-blur-sm`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2 rounded-lg bg-${color}/20 ${textColorClasses[color]}`}>
          {icon}
        </div>
        <div className={`flex items-center gap-1 text-xs font-semibold ${isPositive ? 'text-success' : 'text-danger'}`}>
          <TrendIcon className="w-4 h-4" />
          {Math.abs(trend)}%
        </div>
      </div>

      <p className="text-text-secondary text-xs font-medium mb-2">{title}</p>
      <div className="flex items-baseline gap-1">
        <span className="text-3xl font-bold">{value}</span>
        <span className="text-text-secondary text-sm">{unit}</span>
      </div>
    </div>
  )
}
