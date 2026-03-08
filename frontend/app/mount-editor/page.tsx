'use client'
import { useState } from 'react'
import { DashboardShell } from '@/components/DashboardShell'

const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function MountEditorPage() {
  const [mount, setMount] = useState('/live')
  const [streamName, setStreamName] = useState('Live Radio')
  const [artist, setArtist] = useState('Artist')
  const [title, setTitle] = useState('Track')
  const [result, setResult] = useState('')

  async function saveMount() {
    const r = await fetch(`${api}/api/mounts/upsert`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mount_name: mount, stream_name: streamName, hidden: 0, mp3_metadata_interval: 8192 })
    })
    setResult(JSON.stringify(await r.json(), null, 2))
  }

  async function updateMetadata() {
    const song = `${artist} - ${title}`
    const clean = mount.startsWith('/') ? mount.slice(1) : mount
    const r = await fetch(`${api}/api/mounts/${encodeURIComponent(clean)}/metadata`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ song })
    })
    setResult(JSON.stringify(await r.json(), null, 2))
  }

  return (
    <DashboardShell>
      <h2 className="text-xl mb-4">Mount Configuration Editor</h2>
      <div className="grid md:grid-cols-2 gap-2 mb-3">
        <input className="bg-zinc-900 p-2 rounded" value={mount} onChange={(e) => setMount(e.target.value)} placeholder="/live" />
        <input className="bg-zinc-900 p-2 rounded" value={streamName} onChange={(e) => setStreamName(e.target.value)} placeholder="Stream name" />
      </div>
      <div className="flex gap-2 mb-4">
        <button className="bg-blue-600 px-3 rounded" onClick={saveMount}>Save Mount</button>
      </div>
      <h3 className="font-semibold mb-2">Metadata Update</h3>
      <div className="grid md:grid-cols-2 gap-2 mb-2">
        <input className="bg-zinc-900 p-2 rounded" value={artist} onChange={(e) => setArtist(e.target.value)} placeholder="Artist" />
        <input className="bg-zinc-900 p-2 rounded" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
      </div>
      <button className="bg-emerald-600 px-3 rounded" onClick={updateMetadata}>Push Metadata</button>
      <pre className="text-xs mt-4">{result}</pre>
    </DashboardShell>
  )
}
