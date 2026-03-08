'use client'
import { useEffect, useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function RelaysPage() {
  const [master, setMaster] = useState({ master_server: '', master_server_port: 8000, master_update_interval: 120, master_password: '', relays_on_demand: 1 })
  const [specific, setSpecific] = useState<any[]>([])
  async function load(){ const r=await fetch(`${api}/api/relays`); const j=await r.json(); setSpecific(j.specific||[]) }
  useEffect(()=>{load()},[])
  async function saveMaster(){ await fetch(`${api}/api/relays/master`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(master)}) }
  return <DashboardShell><h2 className="text-xl mb-4">Relay Management</h2><button onClick={saveMaster} className="bg-blue-600 px-3 py-2 rounded mb-4">Save Master Relay</button><ul>{specific.map((r)=> <li key={r.id}>#{r.id} {r.server}:{r.port} {r.mount} → {r['local-mount']}</li>)}</ul></DashboardShell>
}
