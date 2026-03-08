'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function PathsPage(){
  const [result,setResult]=useState('')
  async function save(){ const r=await fetch(`${api}/api/config/bulk-update`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({updates:[{xpath:'paths/allow-ip',value:'/etc/icecast/allowlist.txt'},{xpath:'paths/deny-ip',value:'/etc/icecast/denylist.txt'},{xpath:'paths/ssl-allowed-ciphers',value:'HIGH:!aNULL:!MD5'}]})}); setResult(JSON.stringify(await r.json(),null,2)) }
  return <DashboardShell><h2 className="text-xl mb-4">Paths & Network ACL</h2><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Apply Paths</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
