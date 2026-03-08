'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { DashboardShell } from '@/components/DashboardShell'
import { useStatsStore } from '@/store/useStatsStore'

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function Page() {
  const { listeners, sources, bandwidth, setStats } = useStatsStore()
  const [domain, setDomain] = useState('')
  const [httpsEnabled, setHttpsEnabled] = useState(false)
  const [cloudflare, setCloudflare] = useState(false)
  const [sslMode, setSslMode] = useState('none')
  const [result, setResult] = useState('')

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

  async function saveNginxSettings(e: FormEvent) {
    e.preventDefault()
    const resp = await fetch(`${apiBase}/api/nginx/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, https_enabled: httpsEnabled, cloudflare_enabled: cloudflare, ssl_mode: sslMode, icecast_port: 8000 })
    })
    const body = await resp.json()
    setResult(JSON.stringify(body))
  }

  async function nginxAction(path: string) {
    const resp = await fetch(`${apiBase}/api/nginx/${path}`, { method: path === 'test' ? 'GET' : 'POST' })
    setResult(JSON.stringify(await resp.json()))
  }

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

      <div className="rounded-xl border border-zinc-800 p-4 h-72 mb-6">
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

      <form onSubmit={saveNginxSettings} className="rounded-xl border border-zinc-800 p-4 space-y-3">
        <h3 className="font-semibold">Domain & SSL Control</h3>
        <input className="w-full bg-zinc-900 border border-zinc-700 rounded p-2" placeholder="radio.example.com" value={domain} onChange={(e) => setDomain(e.target.value)} />
        <div className="flex gap-4 text-sm">
          <label><input type="checkbox" checked={httpsEnabled} onChange={(e) => setHttpsEnabled(e.target.checked)} /> Enable HTTPS</label>
          <label><input type="checkbox" checked={cloudflare} onChange={(e) => setCloudflare(e.target.checked)} /> Cloudflare Mode</label>
          <select className="bg-zinc-900 border border-zinc-700 rounded p-1" value={sslMode} onChange={(e) => setSslMode(e.target.value)}>
            <option value="none">No SSL</option>
            <option value="cloudflare">Cloudflare Origin</option>
            <option value="letsencrypt">Let's Encrypt</option>
            <option value="custom">Custom SSL</option>
          </select>
        </div>
        <div className="flex gap-2">
          <button className="bg-blue-600 px-3 py-2 rounded">Save & Reload Nginx</button>
          <button type="button" className="bg-zinc-700 px-3 py-2 rounded" onClick={() => nginxAction('test')}>nginx -t</button>
          <button type="button" className="bg-zinc-700 px-3 py-2 rounded" onClick={() => nginxAction('reload')}>Reload</button>
          <button type="button" className="bg-zinc-700 px-3 py-2 rounded" onClick={() => nginxAction('restart')}>Restart</button>
        </div>
        {result ? <pre className="text-xs bg-zinc-950 p-2 rounded overflow-auto">{result}</pre> : null}
      </form>
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
