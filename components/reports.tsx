'use client'

import { useState, useEffect, useCallback } from 'react'
import { FileText, Download, Search, CheckCircle2, FileSpreadsheet, Eye, Loader2, Sparkles } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface ReportRecord {
  id: string
  title: string
  format: 'PDF' | 'CSV' | 'HTML' | 'JSON'
  size: string
  generatedAt: string
  category: string
  downloadUrl?: string
}

export function Reports() {
  const [searchTerm, setSearchTerm] = useState('')
  const [reports, setReports] = useState<ReportRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadReportsList = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data: any[] = await apiClient.get('/api/v1/reports/list')
      
      // Map API response to UI model
      const mapped = data.map((r: any) => ({
        id: r.id,
        title: r.title,
        format: (r.export_format || 'CSV').toUpperCase() as any,
        size: '14.2 KB', // Mock size representation
        generatedAt: new Date(r.created_at).toLocaleString(),
        category: r.query_executed.toLowerCase().includes('decision') ? 'Strategy Summary' : 'Data Ingestion Audit',
        downloadUrl: r.download_url || undefined,
      }))

      // Standard preloaded default reports for demo purposes
      const preloaded: ReportRecord[] = [
        {
          id: 'rep-1',
          title: 'Q2 Operations Summary & Strategic Recommendations',
          format: 'PDF',
          size: '185 KB',
          generatedAt: '2026-07-05 17:15',
          category: 'Executive Summary'
        },
        {
          id: 'rep-2',
          title: 'Data Profiling & Quality Score Audit (transactions.csv)',
          format: 'CSV',
          size: '1.2 MB',
          generatedAt: '2026-07-05 17:01',
          category: 'Data Quality'
        },
        {
          id: 'rep-3',
          title: 'Singapore Supply Chain Simulation Projection',
          format: 'PDF',
          size: '95 KB',
          generatedAt: '2026-07-04 12:44',
          category: 'Simulation Forecast'
        }
      ]

      setReports([...mapped, ...preloaded])
    } catch (err: any) {
      console.error('Failed to load reports:', err)
      setError('Unable to reach analytics reports database.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadReportsList()
  }, [loadReportsList])

  const handleCompileReport = async () => {
    setGenerating(true)
    try {
      await apiClient.post('/api/v1/reports/generate', {
        title: `Data Quality Profiling Report - ${new Date().toLocaleDateString()}`,
        query_executed: 'SELECT * FROM streamline_dataset.sales_transactions WHERE processed = TRUE',
        export_format: 'csv'
      })
      await loadReportsList()
    } catch (err) {
      console.error('Failed to compile report:', err)
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = (report: ReportRecord) => {
    if (report.downloadUrl) {
      window.open(report.downloadUrl, '_blank')
    } else {
      // Preloaded mockup fallback download helper
      const content = `StreamLine Analytical Report Mockup\nID: ${report.id}\nTitle: ${report.title}\nCategory: ${report.category}\nTimestamp: ${report.generatedAt}`
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${report.title.toLowerCase().replace(/\s+/g, '_')}.${report.format.toLowerCase()}`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const filtered = reports.filter(r => 
    r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.category.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none font-sans">
      {/* Header */}
      <div className="border-b border-border/40 pb-5 flex justify-between items-center w-full">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-sans flex items-center gap-2">
            <FileText className="w-6 h-6 text-accent" />
            <span>Reports Hub</span>
          </h1>
          <p className="text-xs text-muted-foreground mt-1">Access compiled executive summaries, pipeline quality audits, and simulation forecasts.</p>
        </div>
        <button
          onClick={handleCompileReport}
          disabled={generating}
          className="px-3.5 py-1.5 bg-accent hover:bg-accent/90 text-primary-foreground text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 shadow-[0_0_12px_rgba(0,212,255,0.2)] disabled:opacity-50 cursor-pointer border border-accent/20"
        >
          {generating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Compiling Report...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Compile Audit Report</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-500/5 border border-rose-500/10 text-rose-400 rounded-lg text-xs flex justify-between items-center">
          <span>{error}</span>
          <button onClick={loadReportsList} className="underline text-rose-300 hover:text-rose-200 cursor-pointer">Retry</button>
        </div>
      )}

      {/* Filter and Search */}
      <div className="relative group max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/60 group-focus-within:text-accent transition-colors" />
        <input
          type="text"
          placeholder="Search reports by title or type..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-card/60 hover:bg-card border border-border focus:border-accent/40 rounded-lg pl-9 pr-4 py-2.5 text-xs text-slate-100 placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all duration-150"
        />
      </div>

      {/* Reports Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-16">
          <Loader2 className="w-8 h-8 text-accent animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in duration-200">
          {filtered.map((report) => (
            <div 
              key={report.id}
              className="bg-card/40 border border-border/80 hover:border-slate-700 rounded-xl p-5 flex flex-col justify-between gap-4 transition-all duration-200 shadow-sm"
            >
              <div className="flex items-start gap-3.5">
                <div className="p-2.5 rounded-lg bg-muted text-accent border border-white/5 flex items-center justify-center flex-shrink-0">
                  {report.format === 'CSV' ? (
                    <FileSpreadsheet className="w-4.5 h-4.5" />
                  ) : (
                    <FileText className="w-4.5 h-4.5" />
                  )}
                </div>
                <div className="space-y-1.5 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] uppercase tracking-wider font-bold text-accent bg-accent/10 px-2 py-0.5 rounded">
                      {report.category}
                    </span>
                    <span className="text-[10px] text-muted-foreground font-semibold">
                      {report.size}
                    </span>
                  </div>
                  <h3 className="text-xs font-semibold text-slate-200 leading-snug truncate">
                    {report.title}
                  </h3>
                  <p className="text-[10px] text-muted-foreground/60 font-mono">Generated: {report.generatedAt}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 border-t border-border/40 pt-3">
                <button 
                  onClick={() => handleDownload(report)}
                  className="flex items-center gap-1 px-3 py-1.5 border border-accent/40 bg-accent/5 hover:bg-accent/15 text-accent rounded-lg text-[10px] font-bold transition-all cursor-pointer shadow-[0_0_8px_rgba(0,212,255,0.05)]"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Preview</span>
                </button>
                <button 
                  onClick={() => handleDownload(report)}
                  className="flex items-center gap-1 px-3.5 py-1.5 bg-accent hover:bg-accent/90 text-primary-foreground rounded-lg text-[10px] font-bold transition-all shadow-[0_0_10px_rgba(0,212,255,0.3)] border border-accent/20 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download {report.format}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

