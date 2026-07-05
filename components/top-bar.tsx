'use client'

import { useState, useRef } from 'react'
import { Search, Bell, Plus, ChevronDown, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface TopBarProps {
  onChatOpen: () => void
}

export function TopBar({ onChatOpen }: TopBarProps) {
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setStatus('idle')
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      await apiClient.post('/api/v1/upload', formData)
      setStatus('success')
      
      // Dispatch custom event to notify other components to refresh
      window.dispatchEvent(new Event('refresh-decisions'))
      
      setTimeout(() => setStatus('idle'), 3000)
    } catch (err) {
      console.error('File upload failed:', err)
      setStatus('error')
      setTimeout(() => setStatus('idle'), 4000)
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
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
            backgroundColor: status === 'success' ? 'var(--success)' : status === 'error' ? 'var(--danger)' : 'var(--accent)',
            color: 'var(--card)'
          }}
        >
          {uploading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Plus className="w-4 h-4" />
          )}
          {uploading ? 'Uploading...' : status === 'success' ? 'Success!' : status === 'error' ? 'Failed!' : 'Upload Data'}
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
  )
}
