'use client'
import { useEffect, useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'

const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function SocketsPage() {
  const [sockets, setSockets] = useState<any[]>([])
  const [port, setPort] = useState('8000')
  const [bindAddress, setBindAddress] = useState('0.0.0.0')
  const [ssl, setSsl] = useState('0')

  async function load() {
    const r = await fetch(`${api}/api/sockets`)
    const j = await r.json()
    setSockets(j.sockets || [])
  }
  useEffect(() => { load() }, [])

  async function add() {
    await fetch(`${api}/api/sockets`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ port: Number(port), bind_address: bindAddress, ssl: Number(ssl) }) })
    load()
  }

  async function del(id: number) { await fetch(`${api}/api/sockets/${id}`, { method: 'DELETE' }); load() }

  return <DashboardShell><h2 className="text-xl mb-4">Listen Socket Management</h2><div className="flex gap-2 mb-4"><input value={port} onChange={(e)=>setPort(e.target.value)} className="bg-zinc-900 p-2 rounded"/><input value={bindAddress} onChange={(e)=>setBindAddress(e.target.value)} className="bg-zinc-900 p-2 rounded"/><select value={ssl} onChange={(e)=>setSsl(e.target.value)} className="bg-zinc-900 p-2 rounded"><option value="0">ssl 0</option><option value="1">ssl 1</option></select><button onClick={add} className="bg-blue-600 px-3 rounded">Add</button></div><ul className="space-y-2">{sockets.map((s)=> <li key={s.id} className="border border-zinc-800 p-2 rounded flex justify-between"><span>#{s.id} {s.port} {s['bind-address']} ssl={s.ssl}</span><button onClick={()=>del(s.id)} className="text-red-400">Delete</button></li>)}</ul></DashboardShell>
}
