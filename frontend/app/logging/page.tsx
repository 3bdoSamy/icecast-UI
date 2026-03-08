'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function LoggingPage(){
  const [result,setResult]=useState('')
  async function save(){ const r=await fetch(`${api}/api/config/bulk-update`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({updates:[{xpath:'logging/loglevel',value:'4'},{xpath:'logging/logsize',value:'20000'},{xpath:'logging/logarchive',value:'1'}]})}); setResult(JSON.stringify(await r.json(),null,2)) }
  return <DashboardShell><h2 className="text-xl mb-4">Logging Configuration</h2><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Save Logging</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
