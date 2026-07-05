'use client'

import { useState } from 'react'
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
    <div className="fixed bottom-0 right-0 w-96 h-screen md:h-[600px] bg-card border-l border-t border-border rounded-tl-xl flex flex-col shadow-2xl z-50 md:rounded-t-xl md:bottom-4 md:right-4">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div>
          <h3 className="font-bold text-sm">AI Copilot</h3>
          <p className="text-xs text-text-secondary">Always available to help</p>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="p-1 hover:bg-muted rounded-lg transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                msg.sender === 'user'
                  ? 'bg-accent text-card'
                  : 'bg-muted text-foreground'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-muted text-foreground px-4 py-2 rounded-lg flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-accent" />
              <span className="text-sm">DecisionPilot is analyzing...</span>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && !loading && (
        <div className="px-4 py-4 border-t border-border space-y-2">
          <p className="text-xs text-text-secondary mb-3">Try asking:</p>
          <div className="space-y-2">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q)}
                className="w-full text-left text-xs px-3 py-2 bg-muted hover:bg-accent hover:text-card rounded-lg border border-border hover:border-accent transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-border">
        <div className="flex gap-2">
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
            placeholder="Ask me anything..."
            className="flex-1 bg-muted border border-border rounded-lg px-3 py-2 text-sm text-foreground placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="p-2 bg-accent text-card rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
