'use client'

import { useState } from 'react'
import Image from 'next/image'
import { X, Send, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface AIChatProps {
  setIsOpen: (open: boolean) => void
}

interface Message {
  id: number
  text: string
  sender: 'ai' | 'user'
  timestamp: Date
}

export function AIChat({ setIsOpen }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI Decision Copilot. Ask me any questions about inventory, revenue metrics, or decision roots.",
      sender: 'ai',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const suggestedQuestions = [
    'Why did revenue drop?',
    'Explain active inventory shortages',
    'Summarize current opportunities',
    'What are my priority decisions?',
  ]

  const handleSend = async (textToSend?: string) => {
    const queryText = textToSend || input
    if (!queryText.trim()) return

    const userMessage: Message = {
      id: Date.now(),
      text: queryText,
      sender: 'user',
      timestamp: new Date(),
    }
    
    setMessages((prev) => [...prev, userMessage])
    if (!textToSend) setInput('')
    setLoading(true)

    try {
      const chatResponse = await apiClient.post('/api/v1/chat', {
        message: queryText,
        workspace: 'default'
      })

      const fullText = chatResponse.response || 'No response details generated.'
      const words = fullText.split(' ')
      const aiMessageId = Date.now() + 1
      
      // Initialize empty message for streaming effect
      setMessages((prev) => [
        ...prev,
        {
          id: aiMessageId,
          text: '',
          sender: 'ai',
          timestamp: new Date(),
        }
      ])

      let wordIndex = 0
      let typedText = ''
      
      const interval = setInterval(() => {
        if (wordIndex < words.length) {
          typedText += (wordIndex === 0 ? '' : ' ') + words[wordIndex]
          setMessages((prev) =>
            prev.map((m) => (m.id === aiMessageId ? { ...m, text: typedText } : m))
          )
          wordIndex++
        } else {
          clearInterval(interval)
        }
      }, 35) // word-by-word streaming effect

    } catch (err: any) {
      console.error('AIChat interaction failed:', err)
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: `Error connecting to DecisionPilot: ${err?.message || 'Server offline'}. Please check your connection and try again.`,
        sender: 'ai',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div 
      className="fixed bottom-0 right-0 w-full h-full md:w-[380px] md:h-[620px] bg-background border-l border-t border-border/80 rounded-tl-2xl flex flex-col shadow-[0_20px_50px_rgba(0,0,0,0.6)] z-50 md:rounded-2xl md:bottom-6 md:right-6 md:border"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border/60 select-none bg-card/40">
        <div className="flex items-center gap-2.5">
          <div className="relative w-7 h-7 rounded-lg overflow-hidden border border-border/60 flex-shrink-0 bg-background/50 flex items-center justify-center">
            <Image 
              src="/logo.png" 
              alt="StreamLine Logo" 
              fill
              sizes="28px"
              priority
              className="object-contain p-0.5"
            />
          </div>
          <div className="space-y-0.5">
            <h3 className="font-semibold text-xs text-white uppercase tracking-wider flex items-center gap-1.5">
              <span>AI Decision Copilot</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.6)]" />
            </h3>
            <p className="text-[9px] text-muted-foreground/60 leading-none">Autonomous business analytics engine</p>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1.5 text-muted-foreground/50 hover:text-slate-200 hover:bg-white/[0.04] rounded-lg transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-1 fade-in duration-200`}
          >
            <div
              className={`max-w-[85%] text-xs px-3.5 py-2.5 shadow-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-accent/90 to-secondary/90 text-white rounded-2xl rounded-tr-xs font-semibold'
                  : 'bg-card/85 border border-border/40 text-slate-300 rounded-2xl rounded-tl-xs'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start animate-in fade-in duration-100">
            <div className="bg-card/60 border border-white/5 text-muted-foreground px-3 py-2 rounded-2xl rounded-tl-xs flex items-center gap-2 shadow-sm text-xs select-none">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-accent" />
              <span>Analyzing telemetry...</span>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && !loading && (
        <div className="px-4 py-3.5 border-t border-border/60 bg-background/90 space-y-2 select-none">
          <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground/70">Try Asking:</p>
          <div className="flex flex-col gap-1.5">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q)}
                className="w-full text-left text-xs px-3 py-2 bg-card/45 hover:bg-card border border-border/65 hover:border-accent/30 text-muted-foreground hover:text-slate-200 rounded-lg transition-all duration-150 font-medium cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="p-4 border-t border-border/60 bg-card select-none">
        <div className="flex gap-2 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="Ask anything about inventory, revenue..."
            className="flex-1 bg-background border border-border focus:border-accent/40 rounded-lg px-3 py-2.5 text-xs text-slate-100 placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="px-3 bg-secondary hover:bg-secondary/90 text-white rounded-lg transition-all shadow-sm shadow-secondary/20 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none flex items-center justify-center border border-secondary/10 cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}
