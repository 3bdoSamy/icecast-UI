'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function LoggingPage() {
  const [loglevel, setLoglevel] = useState('4')
  const [logsize, setLogsize] = useState('20000')
  const [logarchive, setLogarchive] = useState('1')
  const [result, setResult] = useState('')
  async function save() {
    const r = await fetch(`${api}/api/config/bulk-update`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ updates: [{ xpath: 'logging/loglevel', value: loglevel }, { xpath: 'logging/logsize', value: logsize }, { xpath: 'logging/logarchive', value: logarchive }] }) })
    setResult(JSON.stringify(await r.json(), null, 2))
  }
  return <DashboardShell><h2 className="text-xl mb-4">Logging Configuration</h2><div className="grid md:grid-cols-3 gap-2 mb-3"><input className="bg-zinc-900 p-2 rounded" value={loglevel} onChange={(e)=>setLoglevel(e.target.value)} placeholder="loglevel"/><input className="bg-zinc-900 p-2 rounded" value={logsize} onChange={(e)=>setLogsize(e.target.value)} placeholder="logsize"/><input className="bg-zinc-900 p-2 rounded" value={logarchive} onChange={(e)=>setLogarchive(e.target.value)} placeholder="logarchive"/></div><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Save Logging</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
