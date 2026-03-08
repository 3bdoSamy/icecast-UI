import asyncio
import os
import time
from collections import defaultdict, deque
import httpx
import psutil
import httpx
from fastapi import APIRouter, Depends, WebSocket
from services.security import get_current_user
from services import icecast_controller

router = APIRouter()
ICECAST_STATS_URL = os.getenv('ICECAST_STATS_URL', 'http://127.0.0.1:8000/status-json.xsl')

listener_history = defaultdict(lambda: deque(maxlen=3600))
global_history = deque(maxlen=3600)
_last_net = {'time': None, 'bytes': None}


def _network_bps() -> float:
    now = time.time()
    counters = psutil.net_io_counters()
    total = counters.bytes_sent + counters.bytes_recv
    if _last_net['time'] is None:
        _last_net['time'] = now
        _last_net['bytes'] = total
        return 0.0
    dt = max(now - _last_net['time'], 1e-6)
    db = max(total - (_last_net['bytes'] or 0), 0)
    _last_net['time'] = now
    _last_net['bytes'] = total
    return db / dt


async def _collect_stats():
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.get(ICECAST_STATS_URL)
            payload = response.json()
        except Exception:
            payload = {'icestats': {'listeners': 0, 'source': []}}

    icestats = payload.get('icestats', {})
    sources = icestats.get('source', [])
    if isinstance(sources, dict):
        sources = [sources]

    ts = int(time.time())
    total_listeners = int(icestats.get('listeners', 0) or 0)
    total_bandwidth = float(icestats.get('bandwidth', 0) or 0)
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    bps = _network_bps()

    per_mount = []
    for src in sources:
        mount = src.get('listenurl', src.get('server_name', 'unknown'))
        listeners = int(src.get('listeners', 0) or 0)
        listener_history[mount].append({'ts': ts, 'listeners': listeners})
        per_mount.append({'mount': mount, 'listeners': listeners, 'bitrate': src.get('bitrate', 0)})

    global_history.append({'ts': ts, 'listeners': total_listeners, 'bandwidth': total_bandwidth, 'cpu': cpu, 'ram': mem, 'net_bps': bps})
    top_mounts = sorted(per_mount, key=lambda m: m['listeners'], reverse=True)[:10]

    return {
        'raw': payload,
        'analytics': {
            'cpu_usage': cpu,
            'ram_usage': mem,
            'network_bandwidth_bps': bps,
            'listener_peaks': max((x['listeners'] for x in global_history), default=0),
            'historical_listeners': list(global_history),
            'top_mounts': top_mounts,
            'listener_history_per_mount': {k: list(v) for k, v in listener_history.items()},
        },
    }


@router.post('/start')
ICECAST_STATS_URL = os.getenv("ICECAST_STATS_URL", "http://icecast:8000/status-json.xsl")


@router.post("/start")
def start(_=Depends(get_current_user)):
    return icecast_controller.start_icecast()


@router.post('/stop')
@router.post("/stop")
def stop(_=Depends(get_current_user)):
    return icecast_controller.stop_icecast()


@router.post('/restart')
@router.post("/restart")
def restart(_=Depends(get_current_user)):
    return icecast_controller.restart_icecast()


@router.post('/reload')
def reload(_=Depends(get_current_user)):
    return icecast_controller.reload_icecast()


@router.get('/status')
def status(_=Depends(get_current_user)):
    return icecast_controller.icecast_status()


@router.get('/analytics')
async def analytics(_=Depends(get_current_user)):
    return await _collect_stats()


@router.websocket('/ws/stats')
async def stats_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        payload = await _collect_stats()
@router.websocket("/ws/stats")
async def stats_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.get(ICECAST_STATS_URL)
                payload = response.json()
            except Exception:
                payload = {"icestats": {"listeners": 0, "sources": 0}}
        await websocket.send_json(payload)
        await asyncio.sleep(2)
