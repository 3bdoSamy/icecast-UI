'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'
const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function ListenersPage(){
  const [mount,setMount]=useState('/live')
  const [raw,setRaw]=useState('')
  async function list(){ const r=await fetch(`${api}/api/listeners?mount=${encodeURIComponent(mount)}`); setRaw(JSON.stringify(await r.json(),null,2)) }
  return <DashboardShell><h2 className="text-xl mb-4">Listeners</h2><div className="flex gap-2"><input className="bg-zinc-900 p-2 rounded" value={mount} onChange={(e)=>setMount(e.target.value)}/><button className="bg-blue-600 px-3 rounded" onClick={list}>List</button></div><pre className="text-xs mt-4">{raw}</pre></DashboardShell>
}
