'use client'

import { useState, useRef, useEffect } from 'react'
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
  { name: 'Analyzing & Refresing Feed', progress: 95 },
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
    showToast(`Ingesting ${file.filename || file.name}...`, 'info')

    // Simulate multi-stage progression up to 95% while waiting for API resolution
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
      
      const result = await apiClient.post('/api/v1/upload', formData)
      
      clearInterval(progressInterval)
      setCurrentStageIdx(UPLOAD_STAGES.length - 1) // Ready (100%)
      
      showToast('Dataset Uploaded Successfully!', 'success')
      showToast('Business Analysis Completed & Decision Feed Updated.', 'success')

      // Dispatch custom event to notify other components to refresh
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
        className="px-8 py-4 flex items-center justify-between gap-4"
        style={{
          backgroundColor: 'var(--card)',
          borderBottom: '1px solid var(--border)',
          color: 'var(--foreground)'
        }}
      >
        {/* Left: Search */}
        <div className="flex-1 max-w-md relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
          <input
            type="text"
            placeholder="Search decisions, data, reports..."
            className="w-full border rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
            style={{
              backgroundColor: 'var(--muted)',
              borderColor: 'var(--border)',
              color: 'var(--foreground)',
              '--tw-ring-color': 'var(--accent)'
            } as any}
          />
        </div>

        {/* Hidden file input */}
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          style={{ display: 'none' }} 
          accept=".csv,.xlsx,.xls,.json"
        />

        {/* Right: Workspace Selector, Notifications, Quick Upload, Profile */}
        <div className="flex items-center gap-3">
          {/* Workspace Selector */}
          <button 
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium hover:opacity-80"
            style={{ color: 'var(--foreground)' }}
          >
            <span>Workspace</span>
            <ChevronDown className="w-4 h-4" />
          </button>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg transition-colors hover:opacity-80">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ backgroundColor: 'var(--danger)' }}></span>
          </button>

          {/* Quick Upload */}
          <button
            onClick={handleUploadClick}
            disabled={uploading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium hover:opacity-90 transition-opacity text-sm disabled:opacity-50"
            style={{
              backgroundColor: 'var(--accent)',
              color: 'var(--card)'
            }}
          >
            {uploading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            {uploading ? 'Ingesting...' : 'Upload Data'}
          </button>

          {/* Open Chat Assistant Trigger */}
          <button 
            onClick={onChatOpen}
            className="px-3 py-2 border rounded-lg text-sm transition-colors hover:bg-muted font-medium"
            style={{ borderColor: 'var(--border)' }}
          >
            Chat
          </button>

          {/* Profile */}
          <button className="flex items-center gap-2 w-10 h-10 rounded-lg transition-colors hover:opacity-80">
            <div 
              className="w-8 h-8 rounded-lg bg-gradient-to-br"
              style={{
                backgroundImage: 'linear-gradient(135deg, var(--accent), var(--secondary))'
              }}
            ></div>
          </button>
        </div>
      </div>

      {/* Multistage Upload Overlay */}
      {uploading && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-border p-6 rounded-2xl w-full max-w-md shadow-2xl space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-accent" />
                Processing Business Dataset
              </h3>
            </div>
            
            <div className="space-y-2">
              <div className="w-full bg-muted h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-accent h-full transition-all duration-500 rounded-full"
                  style={{ width: `${UPLOAD_STAGES[currentStageIdx].progress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-text-secondary">
                <span>Stage {currentStageIdx + 1} of {UPLOAD_STAGES.length}</span>
                <span>{UPLOAD_STAGES[currentStageIdx].progress}%</span>
              </div>
            </div>

            {/* Stages Checklist */}
            <div className="space-y-2.5">
              {UPLOAD_STAGES.map((stage, idx) => (
                <div 
                  key={idx} 
                  className={`flex items-center gap-3 text-xs transition-opacity duration-300 ${
                    idx === currentStageIdx 
                      ? 'opacity-100 font-semibold text-accent' 
                      : idx < currentStageIdx 
                      ? 'opacity-80 text-success' 
                      : 'opacity-40'
                  }`}
                >
                  {idx < currentStageIdx ? (
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  ) : idx === currentStageIdx ? (
                    <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
                  ) : (
                    <div className="w-4 h-4 border border-border rounded-full flex-shrink-0"></div>
                  )}
                  <span>{stage.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification Container */}
      <div className="fixed bottom-4 right-4 z-[9999] space-y-2 max-w-sm w-full">
        {toasts.map(toast => (
          <div 
            key={toast.id}
            className={`p-4 rounded-xl shadow-xl flex items-start gap-3 border transition-all animate-in fade-in slide-in-from-bottom-2 ${
              toast.type === 'success' 
                ? 'bg-card text-foreground border-success/30' 
                : toast.type === 'error' 
                ? 'bg-card text-danger border-danger/30' 
                : 'bg-card text-foreground border-border'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
            ) : toast.type === 'error' ? (
              <AlertTriangle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
            ) : (
              <Sparkles className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1 text-xs font-medium">
              {toast.message}
            </div>
            <button 
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="p-0.5 hover:bg-muted rounded"
            >
              <X className="w-3 h-3 text-text-secondary" />
            </button>
          </div>
        ))}
      </div>
    </>
  )
}
