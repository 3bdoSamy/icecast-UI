'use client'
import { useEffect, useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'

const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function RelaysPage() {
  const [masterServer, setMasterServer] = useState('')
  const [masterPort, setMasterPort] = useState('8000')
  const [masterPassword, setMasterPassword] = useState('')
  const [relaysOnDemand, setRelaysOnDemand] = useState('1')
  const [server, setServer] = useState('upstream.example.com')
  const [port, setPort] = useState('8000')
  const [mount, setMount] = useState('/live')
  const [localMount, setLocalMount] = useState('/relay-live')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [relayMeta, setRelayMeta] = useState('1')
  const [onDemand, setOnDemand] = useState('1')
  const [specific, setSpecific] = useState<any[]>([])
  const [result, setResult] = useState('')

  async function load() {
    const r = await fetch(`${api}/api/relays`)
    const j = await r.json()
    setSpecific(j.specific || [])
    if (j.master) {
      setMasterServer(j.master['master-server'] || '')
      setMasterPort(String(j.master['master-server-port'] || '8000'))
      setMasterPassword(j.master['master-password'] || '')
      setRelaysOnDemand(String(j.master['relays-on-demand'] || '1'))
    }
  }
  useEffect(() => { load() }, [])

  async function saveMaster() {
    const r = await fetch(`${api}/api/relays/master`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ master_server: masterServer, master_server_port: Number(masterPort), master_update_interval: 120, master_password: masterPassword, relays_on_demand: Number(relaysOnDemand) }) })
    setResult(JSON.stringify(await r.json(), null, 2))
    load()
  }

  async function addSpecific() {
    const r = await fetch(`${api}/api/relays`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ server, port: Number(port), mount, local_mount: localMount, username, password, relay_shoutcast_metadata: Number(relayMeta), on_demand: Number(onDemand) }) })
    setResult(JSON.stringify(await r.json(), null, 2))
    load()
  }

  async function del(id: number) {
    const r = await fetch(`${api}/api/relays/${id}`, { method: 'DELETE' })
    setResult(JSON.stringify(await r.json(), null, 2))
    load()
  }

  return (
    <DashboardShell>
      <h2 className="text-xl mb-4">Relays</h2>
      <h3 className="font-semibold mb-2">Master Relay</h3>
      <div className="grid md:grid-cols-4 gap-2 mb-2">
        <input className="bg-zinc-900 p-2 rounded" value={masterServer} onChange={(e) => setMasterServer(e.target.value)} placeholder="master-server" />
        <input className="bg-zinc-900 p-2 rounded" value={masterPort} onChange={(e) => setMasterPort(e.target.value)} placeholder="master-port" />
        <input className="bg-zinc-900 p-2 rounded" value={masterPassword} onChange={(e) => setMasterPassword(e.target.value)} placeholder="master-password" />
        <input className="bg-zinc-900 p-2 rounded" value={relaysOnDemand} onChange={(e) => setRelaysOnDemand(e.target.value)} placeholder="relays-on-demand" />
      </div>
      <button onClick={saveMaster} className="bg-blue-600 px-3 py-2 rounded mb-5">Save Master</button>

      <h3 className="font-semibold mb-2">Specific Relay</h3>
      <div className="grid md:grid-cols-4 gap-2 mb-2">
        <input className="bg-zinc-900 p-2 rounded" value={server} onChange={(e) => setServer(e.target.value)} placeholder="server" />
        <input className="bg-zinc-900 p-2 rounded" value={port} onChange={(e) => setPort(e.target.value)} placeholder="port" />
        <input className="bg-zinc-900 p-2 rounded" value={mount} onChange={(e) => setMount(e.target.value)} placeholder="mount" />
        <input className="bg-zinc-900 p-2 rounded" value={localMount} onChange={(e) => setLocalMount(e.target.value)} placeholder="local-mount" />
        <input className="bg-zinc-900 p-2 rounded" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
        <input className="bg-zinc-900 p-2 rounded" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" />
        <input className="bg-zinc-900 p-2 rounded" value={relayMeta} onChange={(e) => setRelayMeta(e.target.value)} placeholder="relay-shoutcast-metadata" />
        <input className="bg-zinc-900 p-2 rounded" value={onDemand} onChange={(e) => setOnDemand(e.target.value)} placeholder="on-demand" />
      </div>
      <button onClick={addSpecific} className="bg-emerald-600 px-3 py-2 rounded mb-4">Add Specific Relay</button>

      <ul className="space-y-2 mb-4">{specific.map((r) => <li key={r.id} className="border border-zinc-800 p-2 rounded flex justify-between"><span>#{r.id} {r.server}:{r.port} {r.mount} → {r['local-mount']}</span><button onClick={() => del(r.id)} className="bg-red-700 px-2 rounded">Delete</button></li>)}</ul>
      <pre className="text-xs">{result}</pre>
    </DashboardShell>
  )
}
