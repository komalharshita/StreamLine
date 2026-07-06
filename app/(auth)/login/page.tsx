'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Sparkles, Loader2, AlertCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

export default function LoginPage() {
  const [email, setEmail] = useState('streamlineuser')
  const [password, setPassword] = useState('streamline')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response: any = await apiClient.post('/api/v1/auth/login', {
        email,
        password,
      })

      const token = response.access_token
      if (token) {
        // Store token in client storage
        localStorage.setItem('access_token', token)
        
        // Write HttpOnly-like client-accessible cookie for Next.js middleware check
        document.cookie = `access_token=${token}; path=/; max-age=604800; SameSite=Strict; Secure`
        
        // Redirect to dashboard page
        window.location.href = '/dashboard'
      } else {
        throw new Error('Authentication token omitted by server.')
      }
    } catch (err: any) {
      console.error('Login failed:', err)
      setError(err?.message || 'Invalid username or password credentials.')
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#09090b] text-foreground font-sans p-4 relative overflow-hidden">
      {/* Background ambient radial gradients */}
      <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-accent/5 blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-secondary/5 blur-[120px]" />

      <div className="w-full max-w-md bg-card/30 backdrop-blur-md border border-border/80 rounded-2xl p-8 space-y-6 shadow-2xl relative">
        {/* Header Logo */}
        <div className="flex flex-col items-center space-y-2 text-center">
          <div className="relative w-12 h-12 mb-2">
            <Image 
              src="/logo.png" 
              alt="StreamLine Logo" 
              fill
              sizes="48px"
              priority
              className="object-contain rounded-lg"
            />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
            <span>Sign In to StreamLine</span>
            <Sparkles className="w-4 h-4 text-accent animate-pulse" />
          </h1>
          <p className="text-xs text-muted-foreground max-w-[280px] leading-relaxed">
            Enter your credentials to access your autonomous decision workspace.
          </p>
        </div>

        {/* Hackathon Demo Account Tip Banner */}
        <div className="p-3.5 bg-accent/5 border border-accent/15 rounded-xl text-slate-300 text-xs leading-relaxed space-y-1">
          <span className="font-semibold text-accent flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 animate-pulse text-accent" />
            Hackathon Demo Account
          </span>
          <p className="text-[11px] text-muted-foreground">
            Username: <strong className="text-slate-200">streamlineuser</strong><br />
            Password: <strong className="text-slate-200">streamline</strong>
          </p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-lg flex items-center gap-2.5 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
              Username or Email
            </label>
            <input
              type="text"
              required
              disabled={loading}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full bg-[#121214] border border-border/60 rounded-lg px-3.5 py-2.5 text-xs text-slate-100 placeholder:text-muted-foreground/40 focus:outline-none focus:border-accent/40 focus:ring-1 focus:ring-accent/20 transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
                Password
              </label>
            </div>
            <input
              type="password"
              required
              disabled={loading}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#121214] border border-border/60 rounded-lg px-3.5 py-2.5 text-xs text-slate-100 placeholder:text-muted-foreground/40 focus:outline-none focus:border-accent/40 focus:ring-1 focus:ring-accent/20 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent hover:bg-accent/90 text-primary-foreground text-xs font-bold py-3 rounded-lg shadow-md hover:shadow-accent/10 transition-all duration-150 flex items-center justify-center gap-2 cursor-pointer border border-accent/20"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authenticating Workspace...</span>
              </>
            ) : (
              <span>Access Account</span>
            )}
          </button>
        </form>

        <div className="text-center text-xs text-muted-foreground border-t border-border/20 pt-4 mt-2">
          <span>New to StreamLine? </span>
          <Link href="/signup" className="text-accent font-semibold hover:underline">
            Register Workspace
          </Link>
        </div>
      </div>
    </div>
  )
}
