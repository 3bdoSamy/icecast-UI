'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function LimitsPage(){
  const [payload,setPayload]=useState({clients:100,sources:10,queue_size:524288,client_timeout:30,header_timeout:15,source_timeout:10,burst_size:65535,burst_on_connect:1})
  const [result,setResult]=useState('')
  async function save(){ const r=await fetch(`${api}/api/config/limits`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); setResult(JSON.stringify(await r.json(),null,2)) }
  return <DashboardShell><h2 className="text-xl mb-4">Limits</h2><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Save Limits</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
