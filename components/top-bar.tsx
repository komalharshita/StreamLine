'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, Bell, Plus, ChevronDown, Loader2, CheckCircle2, AlertTriangle, Sparkles, X, FileText, Database, Shield, Play, ThumbsUp, AlertCircle, Clock } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface TopBarProps {
  onChatOpen: () => void
}

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

interface PreviewData {
  upload_id: string
  preview_rows: any[]
  schema: { name: string; type: string }[]
  statistics: {
    total_rows: number
    total_columns: number
    file_size_bytes: number
    delimiter: string
    encoding: string
    memory_usage: string
    missing_values: Record<string, number>
    duplicate_rows: number
    dtypes: Record<string, string>
    null_percentage: Record<string, number>
    detected_type: string
    confidence: number
    quality_score: number
    quality_report: {
      quality_score: number
      warnings: string[]
      recommendations: string[]
    }
  }
}

interface PipelineStatus {
  status: string
  stage: string
  progress: number
  estimated_time_remaining: string
  elapsed_time: string
  completed_steps: string[]
  error: string | null
}

const STAGES_MAP = [
  { key: 'VALIDATING', label: 'Validating File Size & Format' },
  { key: 'PARSING', label: 'Parsing Dataset Streams' },
  { key: 'ANALYZING', label: 'Auditing Data Quality & Schema' },
  { key: 'IMPORTING', label: 'Cleaning Data & Field Normalization' },
  { key: 'UPLOADING_TO_BIGQUERY', label: 'Ingesting to Google BigQuery Database' },
  { key: 'RUNNING_DECISION_ENGINE', label: 'Evaluating Priority Action Rules' },
  { key: 'GENERATING_METADATA', label: 'Finalizing Metadata Catalog Indexes' }
]

export function TopBar({ onChatOpen }: TopBarProps) {
  const [file, setFile] = useState<File | null>(null)
  
  // Preview Flow States
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [previewData, setPreviewData] = useState<PreviewData | null>(null)
  const [showPreviewModal, setShowPreviewModal] = useState(false)
  
  // Background Processing States
  const [importing, setImporting] = useState(false)
  const [activeUploadId, setActiveUploadId] = useState<string | null>(null)
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null)

  const [toasts, setToasts] = useState<Toast[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Polling Status Tracker
  useEffect(() => {
    if (!importing || !activeUploadId) return

    let pollInterval = setInterval(async () => {
      try {
        const data: PipelineStatus = await apiClient.get(`/api/v1/upload/${activeUploadId}/status`)
        setPipelineStatus(data)

        if (data.status === 'COMPLETED') {
          clearInterval(pollInterval)
          showToast('Dataset Ingested successfully!', 'success')
          showToast('AI analysis completed. Decision feed updated.', 'success')
          window.dispatchEvent(new Event('refresh-decisions'))
          
          setTimeout(() => {
            setImporting(false)
            setActiveUploadId(null)
            setPipelineStatus(null)
          }, 2000)
        } else if (data.status === 'FAILED') {
          clearInterval(pollInterval)
          showToast(`Ingestion Failed: ${data.error || 'Pipeline error'}`, 'error')
        }
      } catch (err: any) {
        console.error('Error polling status:', err)
      }
    }, 800)

    return () => clearInterval(pollInterval)
  }, [importing, activeUploadId])

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    const id = Date.now().toString()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 5000)
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setLoadingPreview(true)
    showToast(`Parsing ${selectedFile.name} preview...`, 'info')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      const data: PreviewData = await apiClient.post('/api/v1/upload/preview', formData)
      setPreviewData(data)
      setShowPreviewModal(true)
    } catch (err: any) {
      console.error('File preview failed:', err)
      showToast(`Preview Failed: ${err?.message || 'Unsupported format'}`, 'error')
    } finally {
      setLoadingPreview(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleConfirmImport = async () => {
    if (!previewData) return

    const uploadId = previewData.upload_id
    setActiveUploadId(uploadId)
    setShowPreviewModal(false)
    setImporting(true)
    setPipelineStatus({
      status: 'IMPORTING',
      stage: 'Importing and Preprocessing',
      progress: 15,
      estimated_time_remaining: '20 seconds',
      elapsed_time: '0 seconds',
      completed_steps: ['VALIDATING', 'PARSING', 'ANALYZING'],
      error: null
    })

    try {
      await apiClient.post('/api/v1/upload/confirm', { upload_id: uploadId })
      showToast('Import triggered in background. Processing pipeline...', 'info')
    } catch (err: any) {
      console.error('Confirmation trigger failed:', err)
      showToast(`Confirmation Failed: ${err?.message || 'Error'}`, 'error')
      setImporting(false)
      setActiveUploadId(null)
      setPipelineStatus(null)
    }
  }

  const formatSize = (bytes: number): string => {
    if (bytes >= 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    }
    return `${(bytes / 1024).toFixed(0)} KB`
  }

  const getQualityColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5'
    if (score >= 60) return 'text-amber-400 border-amber-500/20 bg-amber-500/5'
    return 'text-rose-400 border-rose-500/20 bg-rose-500/5'
  }

  const getQualityBarColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500'
    if (score >= 60) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  return (
    <>
      <div 
        className="px-8 h-16 flex items-center justify-between gap-6 bg-background border-b border-border select-none"
      >
        {/* Search - Command Style */}
        <div className="flex-1 max-w-md relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/60 group-focus-within:text-accent transition-colors" />
          <input
            type="text"
            placeholder="Search decisions, data, reports..."
            className="w-full bg-card/60 hover:bg-card border border-border/80 focus:border-accent/40 rounded-lg pl-9 pr-14 py-2 text-xs text-slate-100 placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all duration-150"
          />
          <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-0.5 px-1.5 py-0.5 bg-muted/80 border border-border/40 rounded text-[9px] font-mono text-muted-foreground/60 select-none">
            <span>⌘</span><span>K</span>
          </div>
        </div>

        {/* Hidden File Input */}
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden"
          accept=".csv,.xlsx,.xls"
        />

        {/* Right Actions */}
        <div className="flex items-center gap-3.5">
          {/* Workspace Select */}
          <button 
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground hover:text-slate-100 hover:bg-white/[0.03] border border-transparent hover:border-border transition-all duration-150 cursor-pointer"
          >
            <span>Default Workspace</span>
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground/60" />
          </button>

          {/* Bell Notifications */}
          <button className="relative p-2 rounded-lg text-muted-foreground hover:text-slate-100 hover:bg-white/[0.03] transition-all duration-150 cursor-pointer">
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-destructive animate-pulse"></span>
          </button>

          <div className="h-4 w-px bg-border/85"></div>

          {/* Chat Copilot Trigger */}
          <button 
            onClick={onChatOpen}
            className="px-3.5 py-2 border border-accent/40 bg-accent/5 hover:bg-accent/15 rounded-lg text-xs font-semibold text-accent transition-all duration-150 cursor-pointer shadow-[0_0_8px_rgba(0,212,255,0.1)]"
          >
            Open Copilot
          </button>

          {/* Quick Upload Button */}
          <button
            onClick={handleUploadClick}
            disabled={loadingPreview || importing}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-accent hover:bg-accent/90 active:scale-95 disabled:opacity-50 text-primary-foreground rounded-lg text-xs font-bold shadow-[0_0_12px_rgba(0,212,255,0.35)] transition-all duration-150 disabled:cursor-not-allowed border border-accent/20 cursor-pointer"
          >
            {loadingPreview ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plus className="w-3.5 h-3.5" />
            )}
            <span>{loadingPreview ? 'Analyzing...' : 'Ingest Data'}</span>
          </button>

          {/* User Profile Avatar */}
          <button className="relative flex items-center justify-center w-8 h-8 rounded-lg overflow-hidden border border-border hover:border-slate-600 transition-colors cursor-pointer">
            <div 
              className="w-full h-full bg-gradient-to-tr from-accent to-secondary"
            />
          </button>
        </div>
      </div>

      {/* 1. Intelligent Dataset Preview & Audit Modal */}
      {showPreviewModal && previewData && file && (
        <div className="fixed inset-0 bg-background/60 backdrop-blur-xs z-50 flex items-center justify-center p-4 overflow-y-auto select-none">
          <div className="bg-card border border-border/80 rounded-2xl w-full max-w-5xl max-h-[85vh] flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-200 overflow-hidden">
            {/* Modal Header */}
            <div className="p-5 border-b border-border/60 flex items-center justify-between">
              <div className="space-y-1">
                <h3 className="font-semibold text-sm text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-accent" />
                  Dataset Preview & Schema Audit: <span className="text-accent">{file.name}</span>
                </h3>
                <p className="text-[10px] text-muted-foreground/60">Review inferred dataset models, quality matrices, and warnings before finalizing db ingestion.</p>
              </div>
              <button 
                onClick={() => setShowPreviewModal(false)}
                className="p-1 text-muted-foreground/50 hover:text-slate-200 hover:bg-white/[0.04] rounded-lg transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Top Stats and Quality Matrix */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Stats list */}
                <div className="bg-background/40 border border-border/60 rounded-xl p-4.5 space-y-3.5">
                  <h4 className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/70 border-b border-border/40 pb-1.5">File Statistics</h4>
                  <div className="grid grid-cols-2 gap-3 text-[11px] font-medium text-slate-300">
                    <div>
                      <p className="text-muted-foreground/50 text-[9px] uppercase font-bold tracking-wider mb-0.5">Total Rows</p>
                      <p className="font-mono text-white text-xs">{previewData.statistics.total_rows.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground/50 text-[9px] uppercase font-bold tracking-wider mb-0.5">Columns Count</p>
                      <p className="font-mono text-white text-xs">{previewData.statistics.total_columns}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground/50 text-[9px] uppercase font-bold tracking-wider mb-0.5">File Size</p>
                      <p className="font-mono text-white text-xs">{formatSize(previewData.statistics.file_size_bytes)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground/50 text-[9px] uppercase font-bold tracking-wider mb-0.5">Format Encoding</p>
                      <p className="font-mono text-white text-xs capitalize">{previewData.statistics.encoding}</p>
                    </div>
                  </div>
                </div>

                {/* Schema Classification */}
                <div className="bg-background/40 border border-border/60 rounded-xl p-4.5 space-y-3">
                  <h4 className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/70 border-b border-border/40 pb-1.5">Dataset Inference Classification</h4>
                  
                  <div className="space-y-3 pt-0.5">
                    <div>
                      <p className="text-muted-foreground/50 text-[9px] uppercase font-bold tracking-wider mb-0.5">Detected Category Schema</p>
                      <p className="text-white text-sm font-bold flex items-center gap-1.5">
                        <Sparkles className="w-4 h-4 text-accent animate-pulse" />
                        {previewData.statistics.detected_type}
                      </p>
                    </div>
                    <div>
                      <div className="flex justify-between text-[9px] text-muted-foreground/70 font-semibold mb-1">
                        <span>Classification Confidence</span>
                        <span className="text-accent font-mono">{(previewData.statistics.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-muted/80 h-1 rounded-full overflow-hidden">
                        <div 
                          className="bg-accent h-full rounded-full" 
                          style={{ width: `${previewData.statistics.confidence * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Quality Score Audit */}
                <div className={`border rounded-xl p-4.5 space-y-3.5 ${getQualityColor(previewData.statistics.quality_score)}`}>
                  <div className="flex items-center justify-between border-b border-white/[0.04] pb-1.5">
                    <h4 className="text-[10px] uppercase font-bold tracking-wider opacity-85">Data Quality Score</h4>
                    <span className="text-[10px] font-bold font-mono">{previewData.statistics.quality_score}/100</span>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="w-full bg-muted/30 h-2 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${getQualityBarColor(previewData.statistics.quality_score)}`} 
                        style={{ width: `${previewData.statistics.quality_score}%` }}
                      ></div>
                    </div>
                    <p className="text-[10px] opacity-75 leading-relaxed">
                      Score evaluated based on missing columns, duplicate row instances, empty headers, and data type inconsistencies.
                    </p>
                  </div>
                </div>
              </div>

              {/* Data Quality Warnings and recommendations */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
                {/* Warnings list */}
                <div className="bg-background/40 border border-border/60 rounded-xl p-4.5 space-y-2.5">
                  <h4 className="text-[10px] uppercase font-bold tracking-wider text-rose-400 border-b border-border/40 pb-1.5">Validation Warnings ({previewData.statistics.quality_report.warnings.length})</h4>
                  {previewData.statistics.quality_report.warnings.length > 0 ? (
                    <ul className="space-y-1.5 max-h-24 overflow-y-auto text-[11px] text-slate-350 list-disc list-inside">
                      {previewData.statistics.quality_report.warnings.map((w, idx) => (
                        <li key={idx} className="leading-relaxed">{w}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-[10px] text-muted-foreground/60 italic">Zero warning anomalies detected in this dataset schema.</p>
                  )}
                </div>

                {/* Recommendations list */}
                <div className="bg-background/40 border border-border/60 rounded-xl p-4.5 space-y-2.5">
                  <h4 className="text-[10px] uppercase font-bold tracking-wider text-accent border-b border-border/40 pb-1.5">Suggested Action Recommendations</h4>
                  {previewData.statistics.quality_report.recommendations.length > 0 ? (
                    <ul className="space-y-1.5 max-h-24 overflow-y-auto text-[11px] text-slate-355 list-disc list-inside">
                      {previewData.statistics.quality_report.recommendations.map((r, idx) => (
                        <li key={idx} className="leading-relaxed">{r}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-[10px] text-muted-foreground/60 italic">Dataset structural checks fully aligned. Ready for zero-imputation load.</p>
                  )}
                </div>
              </div>

              {/* Raw Spreadsheet Preview Grid */}
              <div className="space-y-2">
                <h4 className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/75">Spreadsheet Data Preview (First 25 rows)</h4>
                <div className="border border-border/80 rounded-xl overflow-hidden bg-background/50">
                  <div className="max-h-56 overflow-auto scrollbar-thin">
                    <table className="w-full text-left border-collapse text-[10px] font-mono text-slate-300">
                      <thead className="bg-card border-b border-border sticky top-0 z-10">
                        <tr>
                          <th className="py-2.5 px-3 border-r border-border text-center w-12 text-muted-foreground/60">#</th>
                          {previewData.schema.map((col, idx) => (
                            <th key={idx} className="py-2.5 px-3.5 border-r border-border min-w-[120px]">
                              <p className="text-[11px] font-sans font-bold text-white leading-none">{col.name}</p>
                              <span className="text-[8px] text-muted-foreground/50 tracking-wider uppercase font-bold mt-1 block leading-none">{col.type}</span>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/20">
                        {previewData.preview_rows.map((row, rowIdx) => (
                          <tr key={rowIdx} className="hover:bg-white/[0.01] transition-colors odd:bg-white/[0.005]">
                            <td className="py-2 px-3 border-r border-border text-center text-muted-foreground/50 bg-card/20">{rowIdx + 1}</td>
                            {previewData.schema.map((col, colIdx) => (
                              <td key={colIdx} className="py-2 px-3.5 border-r border-border max-w-[200px] truncate">
                                {String(row[col.name])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Actions Footer */}
            <div className="p-4 border-t border-border/60 bg-background/50 flex justify-end gap-3">
              <button 
                onClick={() => setShowPreviewModal(false)}
                className="px-4 py-2 border border-border bg-card hover:bg-muted text-slate-300 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer"
              >
                Cancel Ingestion
              </button>
              <button 
                onClick={handleConfirmImport}
                className="flex items-center gap-1.5 px-4.5 py-2 bg-accent hover:bg-accent/90 text-primary-foreground rounded-lg text-xs font-bold shadow-[0_0_10px_rgba(0,212,255,0.3)] border border-accent/20 transition-all duration-150 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Confirm Import</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Premium Multistage Async Ingestion Progress Panel (Notion/Snowflake style) */}
      {importing && pipelineStatus && (
        <div className="fixed inset-0 bg-background/50 backdrop-blur-xs z-50 flex items-center justify-center p-4 select-none">
          <div 
            className="bg-card border border-white/10 p-6 rounded-2xl w-full max-w-md shadow-[0_20px_50px_rgba(0,0,0,0.6)] backdrop-blur-md space-y-6 animate-in fade-in zoom-in-95 duration-200"
          >
            {/* Header Stage */}
            <div className="flex justify-between items-start border-b border-white/[0.04] pb-4">
              <div className="space-y-1">
                <h3 className="font-semibold text-sm text-white flex items-center gap-2">
                  {pipelineStatus.status === 'COMPLETED' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : pipelineStatus.status === 'FAILED' ? (
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                  ) : (
                    <Loader2 className="w-4 h-4 animate-spin text-accent" />
                  )}
                  <span>Ingestion Processing Worker</span>
                </h3>
                <p className="text-muted-foreground/60 text-[10px]">Processing database staging structures and metadata indices...</p>
              </div>
              <span className="font-mono text-sm font-bold text-accent">{pipelineStatus.progress}%</span>
            </div>

            {/* Notion style Progress Metrics Block */}
            <div className="grid grid-cols-2 gap-4 bg-background/40 border border-border/80 p-3.5 rounded-xl text-[10px] font-semibold text-slate-350">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground/60" />
                <div>
                  <p className="text-muted-foreground/40 uppercase font-bold tracking-wider text-[8px] mb-0.5">Elapsed Time</p>
                  <p className="text-white font-mono text-[11px]">{pipelineStatus.elapsed_time}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground/60 animate-pulse" />
                <div>
                  <p className="text-muted-foreground/40 uppercase font-bold tracking-wider text-[8px] mb-0.5">Estimated Remaining</p>
                  <p className="text-white font-mono text-[11px]">{pipelineStatus.estimated_time_remaining}</p>
                </div>
              </div>
            </div>

            {/* Glowing progress slider bar */}
            <div className="w-full bg-muted/80 h-2 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 rounded-full ${
                  pipelineStatus.status === 'FAILED' 
                    ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]'
                    : 'bg-accent shadow-[0_0_8px_rgba(0,212,255,0.4)]'
                }`}
                style={{ width: `${pipelineStatus.progress}%` }}
              ></div>
            </div>

            {/* Stages Checklist List */}
            <div className="space-y-2.5 pt-2 border-t border-white/[0.04]">
              {STAGES_MAP.map((stage, idx) => {
                const isCompleted = pipelineStatus.completed_steps.includes(stage.key) || pipelineStatus.status === 'COMPLETED'
                const isCurrent = pipelineStatus.status === stage.key
                const isFailed = pipelineStatus.status === 'FAILED' && pipelineStatus.progress <= (idx + 1) * 15 && !isCompleted

                return (
                  <div 
                    key={idx} 
                    className={`flex items-center gap-3 text-[11px] transition-all duration-150 ${
                      isCurrent 
                        ? 'text-accent font-medium opacity-100' 
                        : isCompleted 
                        ? 'text-emerald-400 opacity-90' 
                        : isFailed
                        ? 'text-rose-400 opacity-100 font-medium'
                        : 'text-muted-foreground/50 opacity-40'
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    ) : isFailed ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-accent flex-shrink-0" />
                    ) : (
                      <div className="w-3.5 h-3.5 border border-muted rounded-full flex-shrink-0" />
                    )}
                    <span>{stage.label}</span>
                  </div>
                )
              })}
            </div>

            {/* Error Message Box */}
            {pipelineStatus.status === 'FAILED' && (
              <div className="p-4 border border-rose-500/10 bg-rose-500/5 text-rose-400 rounded-xl space-y-3 animate-in slide-in-from-top-2">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-[11px] font-bold leading-none">Database Ingestion Failed</p>
                    <p className="text-[10px] opacity-80 leading-relaxed font-mono">{pipelineStatus.error}</p>
                  </div>
                </div>
                <div className="flex justify-end pt-1">
                  <button 
                    onClick={() => {
                      setImporting(false)
                      setActiveUploadId(null)
                      setPipelineStatus(null)
                    }}
                    className="px-2.5 py-1 bg-rose-500 text-white hover:opacity-90 rounded text-[10px] font-bold cursor-pointer"
                  >
                    Close Tracker
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modern Sonner-Style Toast Containers */}
      <div className="fixed bottom-5 right-5 z-[9999] space-y-2.5 max-w-sm w-full select-none pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id}
            className={`pointer-events-auto p-3.5 rounded-xl shadow-2xl flex items-start gap-3 border backdrop-blur-md bg-background/95 transition-all duration-300 transform animate-in slide-in-from-bottom-5 fade-in ${
              toast.type === 'success' 
                ? 'border-emerald-500/20 text-slate-100 shadow-emerald-950/5' 
                : toast.type === 'error' 
                ? 'border-rose-500/20 text-rose-400 shadow-rose-950/5' 
                : 'border-border text-slate-100'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400 flex-shrink-0 mt-0.5" />
            ) : toast.type === 'error' ? (
              <AlertTriangle className="w-4.5 h-4.5 text-rose-400 flex-shrink-0 mt-0.5" />
            ) : (
              <Sparkles className="w-4.5 h-4.5 text-accent flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1 text-[11px] font-medium leading-relaxed">
              {toast.message}
            </div>
            <button 
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="p-0.5 text-muted-foreground/60 hover:text-muted-foreground hover:bg-white/[0.04] rounded transition-colors cursor-pointer"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </>
  )
}
