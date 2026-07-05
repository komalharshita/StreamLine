'use client'

import { useEffect } from 'react'

export default function RootPage() {
  useEffect(() => {
    // Client-side fallback check if middleware is bypassed
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (token) {
      window.location.href = '/dashboard'
    } else {
      window.location.href = '/login'
    }
  }, [])

  return (
    <div className="flex h-screen items-center justify-center bg-[#09090b] text-white">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-t-accent border-r-transparent border-l-transparent animate-spin" />
        <span className="text-xs text-muted-foreground font-mono">Initializing StreamLine...</span>
      </div>
    </div>
  )
}
