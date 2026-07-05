'use client'

import { useState } from 'react'
import { Beaker, Settings2, Sliders, TrendingUp, Zap, HelpCircle } from 'lucide-react'

export function SimulationLab() {
  const [priceAdjust, setPriceAdjust] = useState(0) // -15 to +15 %
  const [marketingBudget, setMarketingBudget] = useState(25) // -50 to +100 %
  const [shippingPriority, setShippingPriority] = useState(250) // 0 to 1000 $

  // Compute mock dynamic metrics based on sliders
  const simulatedHealth = Math.min(100, Math.max(15, 82 + (marketingBudget * 0.15) - (priceAdjust * 0.4) - (shippingPriority * 0.005))).toFixed(0)
  const simulatedROI = (18.5 + (priceAdjust * 0.8) + (marketingBudget * 0.22) - (shippingPriority * 0.008)).toFixed(1)
  const simulatedSavings = Math.round(45000 + (marketingBudget * 950) + (priceAdjust * 1400) - (shippingPriority * 8))

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="border-b border-border/40 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white font-sans flex items-center gap-2">
          <Beaker className="w-6 h-6 text-accent" />
          <span>Simulation Lab</span>
        </h1>
        <p className="text-xs text-muted-foreground mt-1">Evaluate expected forecasting impact, priority scores, and ROI projections via dynamic parameters tuning.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dynamic Variable Sliders */}
        <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-6">
          <div className="flex items-center gap-2 border-b border-border/40 pb-3">
            <Sliders className="w-4.5 h-4.5 text-accent" />
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Simulation Variables</h3>
          </div>

          <div className="space-y-5">
            {/* Price Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-200">Price Adjustment</span>
                <span className="text-accent font-mono">{priceAdjust > 0 ? `+${priceAdjust}` : priceAdjust}%</span>
              </div>
              <input
                type="range"
                min="-15"
                max="15"
                value={priceAdjust}
                onChange={(e) => setPriceAdjust(Number(e.target.value))}
                className="w-full accent-accent bg-muted h-1 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[9px] text-muted-foreground/60">
                <span>Markdown (-15%)</span>
                <span>Markup (+15%)</span>
              </div>
            </div>

            {/* Marketing Budget Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-200">Marketing Allocation</span>
                <span className="text-accent font-mono">{marketingBudget > 0 ? `+${marketingBudget}` : marketingBudget}%</span>
              </div>
              <input
                type="range"
                min="-50"
                max="100"
                value={marketingBudget}
                onChange={(e) => setMarketingBudget(Number(e.target.value))}
                className="w-full accent-accent bg-muted h-1 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[9px] text-muted-foreground/60">
                <span>Deficit (-50%)</span>
                <span>Surplus (+100%)</span>
              </div>
            </div>

            {/* Logistics Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-200">Logistics Priority Buffer</span>
                <span className="text-accent font-mono">${shippingPriority}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1000"
                step="50"
                value={shippingPriority}
                onChange={(e) => setShippingPriority(Number(e.target.value))}
                className="w-full accent-accent bg-muted h-1 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[9px] text-muted-foreground/60">
                <span>Standard Freight</span>
                <span>Air Dispatch ($1K)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Projections Matrix */}
        <div className="lg:col-span-2 space-y-6">
          {/* Output KPIs Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Simulated Health */}
            <div className="bg-card/40 border border-border/80 rounded-xl p-4.5 space-y-2.5">
              <p className="text-muted-foreground/70 text-[10px] uppercase font-bold tracking-wider">Simulated Health Index</p>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold tracking-tight text-white font-mono">{simulatedHealth}</span>
                <span className="text-muted-foreground text-xs font-semibold">%</span>
              </div>
            </div>

            {/* Simulated ROI */}
            <div className="bg-card/40 border border-border/80 rounded-xl p-4.5 space-y-2.5">
              <p className="text-muted-foreground/70 text-[10px] uppercase font-bold tracking-wider">Projected ROI Leverage</p>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold tracking-tight text-white font-mono">{simulatedROI}</span>
                <span className="text-muted-foreground text-xs font-semibold">%</span>
              </div>
            </div>

            {/* Simulated Savings */}
            <div className="bg-card/40 border border-border/80 rounded-xl p-4.5 space-y-2.5">
              <p className="text-muted-foreground/70 text-[10px] uppercase font-bold tracking-wider">Simulated Net Impact</p>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold tracking-tight text-white font-mono">${simulatedSavings.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Simulated Chart Container */}
          <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-5">
            <div className="flex justify-between items-center border-b border-border/40 pb-3">
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">Projected Revenue Impact Chart</h3>
              <span className="text-[9px] uppercase tracking-wider font-bold text-accent bg-accent/10 px-2 py-0.5 rounded">Simulated</span>
            </div>

            {/* Vertical Bar Simulators */}
            <div className="h-32 flex items-end justify-around gap-6 px-4 pt-4">
              {/* Baseline */}
              <div className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-muted h-24 rounded-t-md relative overflow-hidden" />
                <span className="text-[10px] text-muted-foreground font-semibold">Baseline ($2.45M)</span>
              </div>

              {/* Simulated */}
              <div className="flex-1 flex flex-col items-center gap-2 group">
                <div 
                  className="w-full bg-accent rounded-t-md shadow-[0_0_12px_rgba(0,212,255,0.3)] transition-all duration-300 relative overflow-hidden"
                  style={{ height: `${Math.min(100, 75 + (marketingBudget * 0.2) + (priceAdjust * 0.5))}%` }}
                >
                  <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <span className="text-[10px] text-accent font-semibold">Simulated ($2.{(45 + (simulatedSavings/10000)).toFixed(0)}M)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
