'use client'

export function Chart({ title, type }: { title: string; type: 'line' | 'bar' }) {
  return (
    <div 
      className="bg-zinc-900/40 border border-border/80 rounded-xl p-5 space-y-5 select-none shadow-sm"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-white uppercase tracking-wider">{title}</h3>
        <span className="text-[9px] uppercase tracking-wider font-bold text-zinc-500 bg-zinc-900 border border-white/5 px-2 py-0.5 rounded">Live Data</span>
      </div>

      {/* Chart Canvas */}
      <div className="relative pt-2">
        {type === 'line' && (
          <div className="h-48 relative w-full">
            {/* SVG Line Chart */}
            <svg
              viewBox="0 0 400 200"
              className="w-full h-full overflow-visible"
              preserveAspectRatio="none"
            >
              {/* Grids */}
              <line x1="0" y1="200" x2="400" y2="200" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
              <line x1="0" y1="150" x2="400" y2="150" stroke="rgba(255,255,255,0.03)" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="0" y1="100" x2="400" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="0" y1="50" x2="400" y2="50" stroke="rgba(255,255,255,0.03)" strokeWidth="1" strokeDasharray="3 3" />

              {/* Gradient Area Definition */}
              <defs>
                <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity="0.18" />
                  <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Glowing Outline Duplicate */}
              <path
                d="M 10 150 C 30 135, 30 135, 50 120 C 70 105, 70 95, 90 90 C 110 85, 110 115, 130 110 C 150 105, 150 75, 170 70 C 190 65, 190 105, 210 100 C 230 95, 230 65, 250 60 C 270 55, 270 85, 290 80 C 310 75, 310 55, 330 50 C 350 45, 350 70, 370 75"
                fill="none"
                stroke="#6366f1"
                strokeWidth="4.5"
                strokeOpacity="0.15"
                strokeLinecap="round"
              />

              {/* Smooth Bezier Path */}
              <path
                d="M 10 150 C 30 135, 30 135, 50 120 C 70 105, 70 95, 90 90 C 110 85, 110 115, 130 110 C 150 105, 150 75, 170 70 C 190 65, 190 105, 210 100 C 230 95, 230 65, 250 60 C 270 55, 270 85, 290 80 C 310 75, 310 55, 330 50 C 350 45, 350 70, 370 75"
                fill="none"
                stroke="#6366f1"
                strokeWidth="2"
                strokeLinecap="round"
              />

              {/* Area Under Path */}
              <path
                d="M 10 150 C 30 135, 30 135, 50 120 C 70 105, 70 95, 90 90 C 110 85, 110 115, 130 110 C 150 105, 150 75, 170 70 C 190 65, 190 105, 210 100 C 230 95, 230 65, 250 60 C 270 55, 270 85, 290 80 C 310 75, 310 55, 330 50 C 350 45, 350 70, 370 75 L 370 200 L 10 200 Z"
                fill="url(#chartGradient)"
              />

              {/* Glowing Dots */}
              {[10, 50, 90, 130, 170, 210, 250, 290, 330, 370].map((x, i) => {
                const yValues = [150, 120, 90, 110, 70, 100, 60, 80, 50, 75]
                return (
                  <g key={i} className="hover:opacity-100 opacity-80 transition-opacity cursor-pointer">
                    <circle
                      cx={x}
                      cy={yValues[i]}
                      r="4"
                      fill="#6366f1"
                    />
                    <circle
                      cx={x}
                      cy={yValues[i]}
                      r="7"
                      fill="none"
                      stroke="#6366f1"
                      strokeWidth="1.5"
                      strokeOpacity="0.3"
                    />
                  </g>
                )
              })}
            </svg>
          </div>
        )}

        {type === 'bar' && (
          <div className="h-48 flex items-end justify-around gap-3.5 px-2">
            {[65, 45, 78, 52, 88, 61, 73].map((height, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2 group cursor-pointer">
                {/* Visual Bar Card */}
                <div className="w-full relative h-full flex items-end">
                  <div
                    className="w-full bg-zinc-800 hover:bg-indigo-500 rounded-t-md transition-all duration-200 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)] relative overflow-hidden"
                    style={{ height: `${height}%` }}
                  >
                    <div className="absolute inset-0 bg-indigo-500/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
                <span className="text-[10px] text-zinc-500 group-hover:text-zinc-300 font-semibold transition-colors">W{i + 1}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="flex items-center gap-4 pt-3.5 border-t border-border/40 text-[10px] font-semibold text-zinc-500">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_6px_rgba(99,102,241,0.6)]"></span>
          <span className="text-zinc-400">Primary Metric</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-zinc-800 border border-zinc-700"></span>
          <span className="text-zinc-500">Secondary Metric</span>
        </div>
      </div>
    </div>
  )
}
