'use client'

import { useEffect, useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { DashboardShell } from '@/components/DashboardShell'
import { useStatsStore } from '@/store/useStatsStore'

export default function Page() {
  const { listeners, sources, bandwidth, setStats } = useStatsStore()

  useEffect(() => {
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001'}/api/runtime/ws/stats`)
    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data)
      const icestats = parsed.icestats || {}
      setStats({
        listeners: Number(icestats.listeners || 0),
        sources: Number(icestats.source_total || icestats.sources || 0),
        bandwidth: Number(icestats.bandwidth || 0)
      })
    }
    return () => ws.close()
  }, [setStats])

  const data = useMemo(() => [{ name: 'now', listeners, sources, bandwidth }], [listeners, sources, bandwidth])

  return (
    <DashboardShell>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Broadcast Dashboard</h2>
        <span className="text-green-400">Server Online</span>
      </div>
      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <StatCard label="Total Listeners" value={listeners} />
        <StatCard label="Total Sources" value={sources} />
        <StatCard label="Bandwidth" value={bandwidth} />
      </div>
      <div className="rounded-xl border border-zinc-800 p-4 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="listeners" stroke="#22c55e" />
            <Line type="monotone" dataKey="sources" stroke="#3b82f6" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </DashboardShell>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-zinc-800 p-4 bg-zinc-900/40">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className="text-3xl font-semibold">{value}</p>
    </div>
  )
}
