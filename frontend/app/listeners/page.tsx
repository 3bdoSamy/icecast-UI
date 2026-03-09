'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'

const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function ListenersPage() {
  const [mount, setMount] = useState('/live')
  const [raw, setRaw] = useState<any>(null)
  const [moveTo, setMoveTo] = useState('/backup')

  async function list() {
    const r = await fetch(`${api}/api/listeners?mount=${encodeURIComponent(mount)}`)
    setRaw(await r.json())
  }

  async function kick(id: string) {
    await fetch(`${api}/api/listeners/${id}/kick`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mount }) })
    list()
  }

  async function move(id: string) {
    await fetch(`${api}/api/listeners/${id}/move`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mount, destination: moveTo, listener_id: id }) })
    list()
  }

  const text = String(raw?.body || '')
  const ids = Array.from(text.matchAll(/id="(\d+)"/g)).map((m) => m[1])

  return (
    <DashboardShell>
      <h2 className="text-xl mb-4">Listeners</h2>
      <div className="flex gap-2 mb-3">
        <input className="bg-zinc-900 p-2 rounded" value={mount} onChange={(e) => setMount(e.target.value)} />
        <input className="bg-zinc-900 p-2 rounded" value={moveTo} onChange={(e) => setMoveTo(e.target.value)} />
        <button className="bg-blue-600 px-3 rounded" onClick={list}>List</button>
      </div>
      <div className="space-y-2 mb-4">
        {ids.map((id) => (
          <div key={id} className="border border-zinc-800 rounded p-2 flex gap-2 items-center">
            <span className="text-sm">Listener #{id}</span>
            <button className="bg-red-700 px-2 rounded text-sm" onClick={() => kick(id)}>Kick</button>
            <button className="bg-amber-600 px-2 rounded text-sm" onClick={() => move(id)}>Move</button>
          </div>
        ))}
      </div>
      <pre className="text-xs">{JSON.stringify(raw, null, 2)}</pre>
    </DashboardShell>
  )
}
