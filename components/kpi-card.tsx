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

// Map styles statically so Tailwind compiler picks up classes correctly
const iconWrapperClasses = {
  accent: 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/25',
  secondary: 'bg-zinc-800 text-zinc-300 border border-zinc-700/60',
  success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25',
  warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/25',
}

export function KPICard({ title, value, unit, trend, color, icon }: KPICardProps) {
  const isPositive = trend > 0
  const TrendIcon = isPositive ? TrendingUp : TrendingDown

  return (
    <div 
      className="bg-zinc-900/40 hover:bg-zinc-900/60 border border-border/80 hover:border-zinc-700 rounded-xl p-5 flex flex-col justify-between transition-all duration-200 select-none shadow-[0_1px_3px_rgba(0,0,0,0.2)]"
    >
      <div className="flex items-center justify-between mb-3.5">
        <div className={`p-2 rounded-lg ${iconWrapperClasses[color]} flex items-center justify-center`}>
          {icon}
        </div>
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-bold ${
          isPositive 
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25' 
            : 'bg-rose-500/10 text-rose-400 border-rose-500/25'
        }`}>
          <TrendIcon className="w-3.5 h-3.5 flex-shrink-0" />
          <span>{Math.abs(trend)}%</span>
        </div>
      </div>

      <div className="space-y-1">
        <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">{title}</p>
        <div className="flex items-baseline gap-1">
          <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
          <span className="text-zinc-400 text-xs font-semibold">{unit}</span>
        </div>
      </div>
    </div>
  )
}
