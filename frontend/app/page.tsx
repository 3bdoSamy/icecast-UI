'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { DashboardShell } from '@/components/DashboardShell'
import { useStatsStore } from '@/store/useStatsStore'

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

type Schema = Record<string, string[]>

export default function Page() {
  const { listeners, sources, bandwidth, setStats } = useStatsStore()
  const [domain, setDomain] = useState('')
  const [httpsEnabled, setHttpsEnabled] = useState(false)
  const [cloudflare, setCloudflare] = useState(false)
  const [sslMode, setSslMode] = useState('none')
  const [result, setResult] = useState('')
  const [schema, setSchema] = useState<Schema>({})
  const [configValues, setConfigValues] = useState<Record<string, string>>({})
  const [analytics, setAnalytics] = useState<any>({ historical_listeners: [], top_mounts: [] })
  const [streamMount, setStreamMount] = useState('/live')
  const [streamUser, setStreamUser] = useState('source')
  const [streamToken, setStreamToken] = useState('')

  useEffect(() => {
    fetch(`${apiBase}/api/config/schema`).then((r) => r.json()).then((s) => {
      setSchema(s)
      const initial: Record<string, string> = {}
      Object.values(s).flat().forEach((f: string) => (initial[f] = ''))
      setConfigValues(initial)
    }).catch(() => undefined)
  }, [])
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
      const icestats = parsed.raw?.icestats || parsed.icestats || {}
      const icestats = parsed.icestats || {}
      setStats({
        listeners: Number(icestats.listeners || 0),
        sources: Number(icestats.source_total || icestats.sources || 0),
        bandwidth: Number(icestats.bandwidth || 0)
      })
      setAnalytics(parsed.analytics || {})
    }
    return () => ws.close()
  }, [setStats])

  const data = useMemo(() => (analytics.historical_listeners || []).slice(-40).map((x: any) => ({
    ts: new Date((x.ts || 0) * 1000).toLocaleTimeString(), listeners: x.listeners || 0, cpu: x.cpu || 0, ram: x.ram || 0
  })), [analytics])

  async function saveNginxSettings(e: FormEvent) {
    e.preventDefault()
    const resp = await fetch(`${apiBase}/api/nginx/settings`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, https_enabled: httpsEnabled, cloudflare_enabled: cloudflare, ssl_mode: sslMode, icecast_port: 8000 })
    })
    setResult(JSON.stringify(await resp.json(), null, 2))
  }

  async function nginxAction(path: string) {
    const resp = await fetch(`${apiBase}/api/nginx/${path}`, { method: path === 'test' ? 'GET' : 'POST' })
    setResult(JSON.stringify(await resp.json(), null, 2))
  }

  async function saveConfig() {
    const updates = Object.entries(configValues)
      .filter(([, value]) => value !== '')
      .map(([xpath, value]) => ({ xpath, value }))
    const resp = await fetch(`${apiBase}/api/config/bulk-update`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ updates })
    })
    setResult(JSON.stringify(await resp.json(), null, 2))
  }

  async function issueStreamToken() {
    const resp = await fetch(`${apiBase}/api/listener-auth/stream-token`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mount: streamMount, username: streamUser })
    })
    const json = await resp.json()
    setStreamToken(json.token || '')
  }

  return (
    <DashboardShell>
      <div className="flex items-center justify-between mb-6"><h2 className="text-2xl font-bold">Broadcast Dashboard</h2><span className="text-green-400">Server Online</span></div>
      <div className="grid md:grid-cols-5 gap-4 mb-6">
        <StatCard label="Listeners" value={listeners} />
        <StatCard label="Sources" value={sources} />
        <StatCard label="Bandwidth" value={bandwidth} />
        <StatCard label="CPU %" value={Number(analytics.cpu_usage || 0)} />
        <StatCard label="RAM %" value={Number(analytics.ram_usage || 0)} />
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-zinc-800 p-4 h-72">
          <ResponsiveContainer width="100%" height="100%"><LineChart data={data}><XAxis dataKey="ts"/><YAxis/><Tooltip/><Line type="monotone" dataKey="listeners" stroke="#22c55e"/><Line type="monotone" dataKey="cpu" stroke="#f59e0b"/></LineChart></ResponsiveContainer>
        </div>
        <div className="rounded-xl border border-zinc-800 p-4 h-72">
          <ResponsiveContainer width="100%" height="100%"><BarChart data={analytics.top_mounts || []}><XAxis dataKey="mount" hide/><YAxis/><Tooltip/><Bar dataKey="listeners" fill="#3b82f6"/></BarChart></ResponsiveContainer>
          <p className="text-xs text-zinc-400 mt-2">Listener peak: {analytics.listener_peaks || 0}</p>
        </div>
      </div>

      <form onSubmit={saveNginxSettings} className="rounded-xl border border-zinc-800 p-4 space-y-3 mb-6">
        <h3 className="font-semibold">Nginx / Domain / SSL</h3>
        <input className="w-full bg-zinc-900 border border-zinc-700 rounded p-2" placeholder="radio.example.com" value={domain} onChange={(e) => setDomain(e.target.value)} />
        <div className="flex gap-4 text-sm">
          <label><input type="checkbox" checked={httpsEnabled} onChange={(e) => setHttpsEnabled(e.target.checked)} /> HTTPS</label>
          <label><input type="checkbox" checked={cloudflare} onChange={(e) => setCloudflare(e.target.checked)} /> Cloudflare</label>
          <select className="bg-zinc-900 border border-zinc-700 rounded p-1" value={sslMode} onChange={(e) => setSslMode(e.target.value)}><option value="none">none</option><option value="cloudflare">cloudflare</option><option value="letsencrypt">letsencrypt</option><option value="custom">custom</option></select>
        </div>
        <div className="flex gap-2"><button className="bg-blue-600 px-3 py-2 rounded">Save</button><button type="button" className="bg-zinc-700 px-3 py-2 rounded" onClick={() => nginxAction('test')}>nginx -t</button><button type="button" className="bg-zinc-700 px-3 py-2 rounded" onClick={() => nginxAction('reload')}>Reload</button><button type="button" className="bg-zinc-700 px-3 py-2 rounded" onClick={() => nginxAction('restart')}>Restart</button></div>
      </form>

      <div className="rounded-xl border border-zinc-800 p-4 space-y-3 mb-6">
        <h3 className="font-semibold">Icecast Full Configuration Editor (all sections)</h3>
        {Object.entries(schema).map(([section, fields]) => (
          <div key={section} className="border border-zinc-800 rounded p-3">
            <p className="font-medium mb-2">{section}</p>
            <div className="grid md:grid-cols-2 gap-2">
              {(fields as string[]).map((field) => (
                <label key={field} className="text-xs">
                  <span className="text-zinc-400">{field}</span>
                  <input className="w-full bg-zinc-900 border border-zinc-700 rounded p-2" value={configValues[field] || ''} onChange={(e) => setConfigValues((prev) => ({ ...prev, [field]: e.target.value }))} />
                </label>
              ))}
            </div>
          </div>
        ))}
        <button className="bg-emerald-600 px-3 py-2 rounded" onClick={saveConfig}>Backup + Validate + Apply XML</button>
      </div>

      <div className="rounded-xl border border-zinc-800 p-4 space-y-3">
        <h3 className="font-semibold">Stream Token Authentication</h3>
        <div className="grid md:grid-cols-3 gap-2">
          <input className="bg-zinc-900 border border-zinc-700 rounded p-2" value={streamMount} onChange={(e) => setStreamMount(e.target.value)} placeholder="/live" />
          <input className="bg-zinc-900 border border-zinc-700 rounded p-2" value={streamUser} onChange={(e) => setStreamUser(e.target.value)} placeholder="username" />
          <button className="bg-violet-600 rounded p-2" onClick={issueStreamToken}>Issue Token</button>
        </div>
        {streamToken ? <pre className="text-xs bg-zinc-950 p-2 rounded overflow-auto">{streamToken}</pre> : null}
      </div>

      {result ? <pre className="text-xs bg-zinc-950 p-2 rounded overflow-auto mt-6">{result}</pre> : null}
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
  return <div className="rounded-xl border border-zinc-800 p-4 bg-zinc-900/40"><p className="text-sm text-zinc-400">{label}</p><p className="text-3xl font-semibold">{Math.round(value)}</p></div>
  return (
    <div className="rounded-xl border border-zinc-800 p-4 bg-zinc-900/40">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className="text-3xl font-semibold">{value}</p>
    </div>
  )
}
