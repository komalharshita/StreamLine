'use client'

import { useState } from 'react'
import { Database, Server, HardDrive, RefreshCw, Layers, ShieldAlert, Cpu } from 'lucide-react'

interface SchemaRecord {
  tableId: string
  dataset: string
  rowCount: number
  colCount: number
  storageClass: 'Standard Clustered' | 'Standard partitioned'
  lastSync: string
}

export function DataCenter() {
  const [syncing, setSyncing] = useState(false)
  const [schemas, setSchemas] = useState<SchemaRecord[]>([
    {
      tableId: 'sales_table',
      dataset: 'streamline_analytics',
      rowCount: 1250,
      colCount: 12,
      storageClass: 'Standard Clustered',
      lastSync: '2026-07-05 17:01'
    },
    {
      tableId: 'inventory_table',
      dataset: 'streamline_analytics',
      rowCount: 4500,
      colCount: 8,
      storageClass: 'Standard Clustered',
      lastSync: '2026-07-05 17:01'
    },
    {
      tableId: 'transactions_table',
      dataset: 'streamline_analytics',
      rowCount: 9800,
      colCount: 15,
      storageClass: 'Standard partitioned',
      lastSync: '2026-07-05 17:01'
    }
  ])

  const handleSync = () => {
    setSyncing(true)
    setTimeout(() => {
      setSyncing(false)
      setSchemas(prev => prev.map(s => ({
        ...s,
        lastSync: 'Just now'
      })))
    }, 1500)
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="border-b border-border/40 pb-5 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-sans flex items-center gap-2">
            <Database className="w-6 h-6 text-accent" />
            <span>Data Center</span>
          </h1>
          <p className="text-xs text-muted-foreground mt-1">Manage BigQuery schemas, cloud storage sync adapters, and tabular database partitions.</p>
        </div>
        <button 
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-1.5 px-3.5 py-2 bg-secondary hover:bg-secondary/90 text-white rounded-lg text-xs font-semibold shadow-sm transition-all duration-150 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Syncing...' : 'Sync Tables'}</span>
        </button>
      </div>

      {/* Database Adapter Statuses */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* BigQuery Adapter */}
        <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300">
              <Server className="w-4 h-4 text-accent" />
              <span className="text-xs font-bold uppercase tracking-wider">BigQuery DB</span>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.6)]"></span>
          </div>
          <p className="text-xl font-bold tracking-tight text-slate-200 font-mono">Connected</p>
          <p className="text-[10px] text-muted-foreground">Adapter: GCPClientFactory Singleton</p>
        </div>

        {/* Cloud Storage Adapter */}
        <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300">
              <HardDrive className="w-4 h-4 text-accent" />
              <span className="text-xs font-bold uppercase tracking-wider">GCS Buckets</span>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.6)]"></span>
          </div>
          <p className="text-xl font-bold tracking-tight text-slate-200 font-mono">19.04 MB</p>
          <p className="text-[10px] text-muted-foreground">Bucket: target-sandbox-storage</p>
        </div>

        {/* Security Access Status */}
        <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300">
              <Cpu className="w-4 h-4 text-accent" />
              <span className="text-xs font-bold uppercase tracking-wider">Auth Session</span>
            </div>
            <span className="w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.6)]"></span>
          </div>
          <p className="text-xl font-bold tracking-tight text-slate-200 font-mono">Mock Auth</p>
          <p className="text-[10px] text-muted-foreground">Active Flag: FIREBASE_MOCK_AUTH</p>
        </div>
      </div>

      {/* Target Table Schema List */}
      <div className="bg-card/40 border border-border/80 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-border/40 pb-3">
          <h3 className="text-xs font-semibold text-white uppercase tracking-wider">BigQuery Schema Targets</h3>
          <span className="text-[9px] uppercase tracking-wider font-bold text-accent bg-accent/10 px-2 py-0.5 rounded">3 Tables</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border/40 text-muted-foreground text-[10px] uppercase font-bold tracking-wider">
                <th className="py-2.5">Dataset Name</th>
                <th className="py-2.5">Table ID</th>
                <th className="py-2.5">Record Indices</th>
                <th className="py-2.5">Columns Count</th>
                <th className="py-2.5">Storage Class</th>
                <th className="py-2.5 text-right">Last Sync</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20">
              {schemas.map((s, idx) => (
                <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                  <td className="py-3 text-muted-foreground font-mono text-[10px]">{s.dataset}</td>
                  <td className="py-3 font-semibold text-slate-200">{s.tableId}</td>
                  <td className="py-3 font-mono text-slate-350">{s.rowCount.toLocaleString()} rows</td>
                  <td className="py-3 text-slate-350">{s.colCount} fields</td>
                  <td className="py-3 text-muted-foreground">{s.storageClass}</td>
                  <td className="py-3 text-right text-muted-foreground font-mono text-[10px]">{s.lastSync}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
