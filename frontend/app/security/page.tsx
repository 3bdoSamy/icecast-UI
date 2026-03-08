'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function SecurityPage(){
  const [result,setResult]=useState('')
  async function save(){ const r=await fetch(`${api}/api/config/bulk-update`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({updates:[{xpath:'security/chroot',value:'0'},{xpath:'security/changeowner/user',value:'icecast'},{xpath:'security/changeowner/group',value:'icecast'}]})}); setResult(JSON.stringify(await r.json(),null,2)) }
  return <DashboardShell><h2 className="text-xl mb-4">Security Configuration</h2><button className="bg-blue-600 px-3 py-2 rounded" onClick={save}>Save Security</button><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
