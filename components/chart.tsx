'use client'

export function Chart({ title, type }: { title: string; type: 'line' | 'bar' }) {
  return (
    <div className="bg-card border border-border rounded-xl p-6">
      <h3 className="text-lg font-bold mb-6">{title}</h3>

      {/* Simple Chart Visualization */}
      <div className="space-y-4">
        {type === 'line' && (
          <div className="h-64 relative">
            {/* SVG Line Chart */}
            <svg
              viewBox="0 0 400 200"
              className="w-full h-full"
              preserveAspectRatio="none"
            >
              {/* Grid */}
              <line x1="0" y1="200" x2="400" y2="200" stroke="rgba(255,255,255,0.1)" />
              <line x1="0" y1="150" x2="400" y2="150" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="100" x2="400" y2="100" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="50" x2="400" y2="50" stroke="rgba(255,255,255,0.05)" />

              {/* Gradient Area */}
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#00D4FF" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#00D4FF" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Line */}
              <polyline
                points="10,150 50,120 90,90 130,110 170,70 210,100 250,60 290,80 330,50 370,75"
                fill="none"
                stroke="#00D4FF"
                strokeWidth="2"
              />

              {/* Area */}
              <polygon
                points="10,150 50,120 90,90 130,110 170,70 210,100 250,60 290,80 330,50 370,75 370,200 10,200"
                fill="url(#gradient)"
              />

              {/* Points */}
              {[10, 50, 90, 130, 170, 210, 250, 290, 330, 370].map((x, i) => {
                const yValues = [150, 120, 90, 110, 70, 100, 60, 80, 50, 75]
                return (
                  <circle
                    key={i}
                    cx={x}
                    cy={yValues[i]}
                    r="3"
                    fill="#00D4FF"
                  />
                )
              })}
            </svg>
          </div>
        )}

        {type === 'bar' && (
          <div className="h-64 flex items-end justify-around gap-2 px-4">
            {[65, 45, 78, 52, 88, 61, 73].map((height, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div
                  className="w-full bg-gradient-to-t from-accent to-secondary rounded-t-lg transition-all hover:opacity-80"
                  style={{ height: `${height}%` }}
                ></div>
                <span className="text-xs text-text-secondary">W{i + 1}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-6 pt-4 border-t border-border text-sm text-text-secondary">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-accent"></div>
          <span>Primary Metric</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-secondary"></div>
          <span>Secondary Metric</span>
        </div>
      </div>
    </div>
  )
}
