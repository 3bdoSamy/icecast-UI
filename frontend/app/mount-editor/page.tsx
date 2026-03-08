'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function MountEditorPage(){
  const [mount,setMount]=useState('/live')
  const [streamName,setStreamName]=useState('Live Radio')
  const [result,setResult]=useState('')
  async function save(){
    const r=await fetch(`${api}/api/mounts/upsert`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mount_name:mount,stream_name:streamName,hidden:0,mp3_metadata_interval:8192})})
    setResult(JSON.stringify(await r.json(),null,2))
  }
  return <DashboardShell><h2 className="text-xl mb-4">Mount Configuration Editor</h2><div className="flex gap-2"><input className="bg-zinc-900 p-2 rounded" value={mount} onChange={(e)=>setMount(e.target.value)}/><input className="bg-zinc-900 p-2 rounded" value={streamName} onChange={(e)=>setStreamName(e.target.value)}/><button className="bg-blue-600 px-3 rounded" onClick={save}>Save</button></div><pre className="text-xs mt-4">{result}</pre></DashboardShell>
}
