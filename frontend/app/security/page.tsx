'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function SecurityPage() {
  const [chroot, setChroot] = useState('0')
  const [user, setUser] = useState('icecast')
  const [group, setGroup] = useState('icecast')
  const [result, setResult] = useState('')
  async function save() {
    const r = await fetch(`${api}/api/config/bulk-update`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ updates: [{ xpath: 'security/chroot', value: chroot }, { xpath: 'security/changeowner/user', value: user }, { xpath: 'security/changeowner/group', value: group }] }) })
    setResult(JSON.stringify(await r.json(), null, 2))
  }
  return <DashboardShell><h2 className="text-xl mb-4">Security Configuration</h2><div className="grid md:grid-cols-3 gap-2 mb-3"><input className="bg-zinc-900 p-2 rounded" value={chroot} onChange={(e)=>setChroot(e.target.value)} placeholder="chroot"/><input className="bg-zinc-900 p-2 rounded" value={user} onChange={(e)=>setUser(e.target.value)} placeholder="changeowner user"/><input className="bg-zinc-900 p-2 rounded" value={group} onChange={(e)=>setGroup(e.target.value)} placeholder="changeowner group"/></div><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Save Security</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
