'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function PathsPage() {
  const [values, setValues] = useState({ basedir: '/usr/local/share/icecast', logdir: '/var/log/icecast', pidfile: '/var/run/icecast.pid', webroot: '/usr/local/share/icecast/web', adminroot: '/usr/local/share/icecast/admin', allow_ip: '/etc/icecast/allowlist.txt', deny_ip: '/etc/icecast/denylist.txt', ssl_certificate: '/etc/ssl/certs/cloudflare-origin.pem', alias_source: '/status', alias_destination: '/status.xsl' })
  const [result, setResult] = useState('')
  async function save() {
    const updates = [
      { xpath: 'paths/basedir', value: values.basedir }, { xpath: 'paths/logdir', value: values.logdir }, { xpath: 'paths/pidfile', value: values.pidfile },
      { xpath: 'paths/webroot', value: values.webroot }, { xpath: 'paths/adminroot', value: values.adminroot }, { xpath: 'paths/allow-ip', value: values.allow_ip }, { xpath: 'paths/deny-ip', value: values.deny_ip },
      { xpath: 'paths/ssl-certificate', value: values.ssl_certificate }, { xpath: 'paths/alias/source', value: values.alias_source }, { xpath: 'paths/alias/destination', value: values.alias_destination }
    ]
    const r = await fetch(`${api}/api/config/bulk-update`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ updates }) })
    setResult(JSON.stringify(await r.json(), null, 2))
  }
  return <DashboardShell><h2 className="text-xl mb-4">Paths & SSL</h2><div className="grid md:grid-cols-2 gap-2 mb-3">{Object.entries(values).map(([k,v])=><input key={k} className="bg-zinc-900 p-2 rounded" value={v} onChange={(e)=>setValues((p:any)=>({...p,[k]:e.target.value}))} placeholder={k}/>)}</div><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Apply Paths</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
