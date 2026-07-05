'use client'

import { useState, useRef } from 'react'
import { Search, Bell, Plus, ChevronDown, Loader2, CheckCircle2, AlertTriangle, Sparkles, X } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface TopBarProps {
  onChatOpen: () => void
}

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

const UPLOAD_STAGES = [
  { name: 'Uploading File', progress: 10 },
  { name: 'Validating Format', progress: 25 },
  { name: 'Cleaning Data & Normalizing', progress: 45 },
  { name: 'Uploading to Cloud Storage', progress: 65 },
  { name: 'Loading Google BigQuery', progress: 80 },
  { name: 'Analyzing & Refreshing Feed', progress: 95 },
  { name: 'Ready', progress: 100 }
]

export function TopBar({ onChatOpen }: TopBarProps) {
  const [uploading, setUploading] = useState(false)
  const [currentStageIdx, setCurrentStageIdx] = useState(0)
  const [toasts, setToasts] = useState<Toast[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setCurrentStageIdx(0)
    showToast(`Ingesting ${file.name}...`, 'info')

    let stageIndex = 0
    const progressInterval = setInterval(() => {
      if (stageIndex < UPLOAD_STAGES.length - 2) {
        stageIndex++
        setCurrentStageIdx(stageIndex)
      }
    }, 1800)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      await apiClient.post('/api/v1/upload', formData)
      
      clearInterval(progressInterval)
      setCurrentStageIdx(UPLOAD_STAGES.length - 1)
      
      showToast('Dataset Ingested successfully!', 'success')
      showToast('Business Analysis completed. Decision feed updated.', 'success')

      window.dispatchEvent(new Event('refresh-decisions'))

      setTimeout(() => {
        setUploading(false)
      }, 1000)
    } catch (err: any) {
      clearInterval(progressInterval)
      console.error('File upload failed:', err)
      showToast(`Upload Failed: ${err?.message || 'Connection lost'}`, 'error')
      setUploading(false)
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <>
      <div 
        className="px-8 h-16 flex items-center justify-between gap-6 bg-background border-b border-border select-none"
      >
        {/* Search - Command Style */}
        <div className="flex-1 max-w-md relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-indigo-400 transition-colors" />
          <input
            type="text"
            placeholder="Search decisions, data, reports..."
            className="w-full bg-zinc-900/60 hover:bg-zinc-900 border border-border/80 focus:border-accent/40 rounded-lg pl-9 pr-14 py-2 text-xs text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all duration-150"
          />
          <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-0.5 px-1.5 py-0.5 bg-zinc-800/80 border border-border/40 rounded text-[9px] font-mono text-zinc-500 select-none">
            <span>⌘</span><span>K</span>
          </div>
        </div>

        {/* Hidden File Input */}
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden"
          accept=".csv,.xlsx,.xls,.json"
        />

        {/* Right Actions */}
        <div className="flex items-center gap-3.5">
          {/* Workspace Select */}
          <button 
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.03] border border-transparent hover:border-border transition-all duration-150"
          >
            <span>Default Workspace</span>
            <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
          </button>

          {/* Bell Notifications */}
          <button className="relative p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.03] transition-all duration-150">
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-destructive animate-pulse"></span>
          </button>

          <div className="h-4 w-px bg-border/80"></div>

          {/* Chat Copilot Trigger */}
          <button 
            onClick={onChatOpen}
            className="px-3.5 py-2 border border-border bg-zinc-900/60 hover:bg-zinc-900 rounded-lg text-xs font-semibold text-zinc-200 transition-all duration-150 hover:border-zinc-700 active:bg-zinc-800"
          >
            Open Copilot
          </button>

          {/* Quick Upload Button */}
          <button
            onClick={handleUploadClick}
            disabled={uploading}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-sm shadow-indigo-900/10 hover:shadow-indigo-500/10 transition-all duration-150 disabled:cursor-not-allowed border border-indigo-500/10"
          >
            {uploading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plus className="w-3.5 h-3.5" />
            )}
            <span>{uploading ? 'Ingesting...' : 'Ingest Data'}</span>
          </button>

          {/* User Profile Avatar */}
          <button className="relative flex items-center justify-center w-8 h-8 rounded-lg overflow-hidden border border-border hover:border-zinc-600 transition-colors">
            <div 
              className="w-full h-full bg-gradient-to-tr from-indigo-500 to-violet-500"
            />
          </button>
        </div>
      </div>

      {/* Multistage Ingestion Overlay (Refined Glassmorphic Panel) */}
      {uploading && (
        <div className="fixed inset-0 bg-background/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div 
            className="bg-zinc-900/90 border border-white/10 p-6 rounded-2xl w-full max-w-sm shadow-[0_12px_40px_rgba(0,0,0,0.6)] backdrop-blur-md space-y-5 animate-in fade-in zoom-in-95 duration-200"
          >
            <div className="space-y-1">
              <h3 className="font-semibold text-sm text-white flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-accent" />
                Ingesting Data Pipeline
              </h3>
              <p className="text-zinc-500 text-[10px]">Processing and mapping database aggregates...</p>
            </div>
            
            {/* Progress Bar */}
            <div className="space-y-1.5">
              <div className="w-full bg-zinc-800/80 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-indigo-500 h-full transition-all duration-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]"
                  style={{ width: `${UPLOAD_STAGES[currentStageIdx].progress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-[10px] text-zinc-400 font-medium">
                <span>Stage {currentStageIdx + 1} of {UPLOAD_STAGES.length}</span>
                <span>{UPLOAD_STAGES[currentStageIdx].progress}%</span>
              </div>
            </div>

            {/* Stages Checkbox List */}
            <div className="space-y-2 pt-2 border-t border-white/[0.04]">
              {UPLOAD_STAGES.map((stage, idx) => {
                const isCompleted = idx < currentStageIdx
                const isCurrent = idx === currentStageIdx
                return (
                  <div 
                    key={idx} 
                    className={`flex items-center gap-2.5 text-[11px] transition-all duration-150 ${
                      isCurrent 
                        ? 'text-indigo-400 font-medium opacity-100' 
                        : isCompleted 
                        ? 'text-emerald-400 opacity-90' 
                        : 'text-zinc-500 opacity-40'
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400 flex-shrink-0" />
                    ) : (
                      <div className="w-3.5 h-3.5 border border-zinc-700 rounded-full flex-shrink-0" />
                    )}
                    <span>{stage.name}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Modern Sonner-Style Toast Containers */}
      <div className="fixed bottom-5 right-5 z-[9999] space-y-2.5 max-w-sm w-full select-none pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id}
            className={`pointer-events-auto p-3.5 rounded-xl shadow-2xl flex items-start gap-3 border backdrop-blur-md bg-zinc-950/95 transition-all duration-300 transform animate-in slide-in-from-bottom-5 fade-in ${
              toast.type === 'success' 
                ? 'border-emerald-500/20 text-zinc-100 shadow-emerald-950/5' 
                : toast.type === 'error' 
                ? 'border-rose-500/20 text-rose-400 shadow-rose-950/5' 
                : 'border-border text-zinc-100'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-4.5 h-4.5 text-emerald-400 flex-shrink-0 mt-0.5" />
            ) : toast.type === 'error' ? (
              <AlertTriangle className="w-4.5 h-4.5 text-rose-400 flex-shrink-0 mt-0.5" />
            ) : (
              <Sparkles className="w-4.5 h-4.5 text-indigo-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1 text-[11px] font-medium leading-relaxed">
              {toast.message}
            </div>
            <button 
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="p-0.5 text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04] rounded transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </>
  )
}
