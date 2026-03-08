'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function LimitsPage() {
  const [payload, setPayload] = useState({ clients: 100, sources: 10, queue_size: 524288, header_timeout: 15, source_timeout: 10, burst_size: 65535, burst_on_connect: 1, client_timeout: 30 })
  const [result, setResult] = useState('')
  async function save() {
    const r = await fetch(`${api}/api/config/limits`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    setResult(JSON.stringify(await r.json(), null, 2))
  }
  return <DashboardShell><h2 className="text-xl mb-4">Limits</h2><div className="grid md:grid-cols-4 gap-2 mb-3">{Object.entries(payload).map(([k,v]) => <input key={k} className="bg-zinc-900 p-2 rounded" value={v} onChange={(e)=>setPayload((p:any)=>({...p,[k]:Number(e.target.value)}))} placeholder={k}/>)}</div><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Save Limits</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
