'use client'
import { useEffect, useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'

const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function SocketsPage() {
  const [sockets, setSockets] = useState<any[]>([])
  const [port, setPort] = useState('8000')
  const [bindAddress, setBindAddress] = useState('0.0.0.0')
  const [ssl, setSsl] = useState('0')
  const [shoutcastMount, setShoutcastMount] = useState('/stream')
  const [domain, setDomain] = useState('localhost')
  const [result, setResult] = useState('')

  async function load() {
    const r = await fetch(`${api}/api/sockets`)
    const j = await r.json()
    setSockets(j.sockets || [])
  }

  useEffect(() => { load() }, [])

  async function add() {
    await fetch(`${api}/api/sockets`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ port: Number(port), bind_address: bindAddress, ssl: Number(ssl), shoutcast_mount: shoutcastMount }) })
    load()
  }

  async function update(id: number) {
    await fetch(`${api}/api/sockets/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ port: Number(port), bind_address: bindAddress, ssl: Number(ssl), shoutcast_mount: shoutcastMount }) })
    load()
  }

  async function del(id: number) {
    await fetch(`${api}/api/sockets/${id}`, { method: 'DELETE' })
    load()
  }

  async function syncPrimary() {
    const r = await fetch(`${api}/api/sync/services`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, icecast_port: Number(port), https_enabled: false, ssl_mode: 'none', cloudflare_enabled: false })
    })
    setResult(JSON.stringify(await r.json(), null, 2))
  }

  return (
    <DashboardShell>
      <h2 className="text-xl mb-4">Sockets</h2>
      <div className="grid md:grid-cols-5 gap-2 mb-3">
        <input className="bg-zinc-900 p-2 rounded" value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="domain" />
        <input className="bg-zinc-900 p-2 rounded" value={port} onChange={(e) => setPort(e.target.value)} placeholder="port" />
        <input className="bg-zinc-900 p-2 rounded" value={bindAddress} onChange={(e) => setBindAddress(e.target.value)} placeholder="bind-address" />
        <select className="bg-zinc-900 p-2 rounded" value={ssl} onChange={(e) => setSsl(e.target.value)}><option value="0">ssl 0</option><option value="1">ssl 1</option></select>
        <input className="bg-zinc-900 p-2 rounded" value={shoutcastMount} onChange={(e) => setShoutcastMount(e.target.value)} placeholder="shoutcast-mount" />
      </div>
      <div className="flex gap-2 mb-4">
        <button onClick={add} className="bg-blue-600 px-3 rounded">Add</button>
        <button onClick={syncPrimary} className="bg-emerald-600 px-3 rounded">Sync services()</button>
      </div>
      <ul className="space-y-2">{sockets.map((s) => (
        <li key={s.id} className="border border-zinc-800 p-2 rounded flex items-center justify-between">
          <span>#{s.id} port={s.port} bind={s['bind-address']} ssl={s.ssl} shoutcast={s['shoutcast-mount']}</span>
          <div className="flex gap-2"><button onClick={() => update(s.id)} className="bg-amber-600 px-2 rounded">Update</button><button onClick={() => del(s.id)} className="bg-red-700 px-2 rounded">Delete</button></div>
        </li>
      ))}</ul>
      <pre className="text-xs mt-4">{result}</pre>
    </DashboardShell>
  )
}
