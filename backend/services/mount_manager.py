import os
import httpx

ICECAST_ADMIN_URL = os.getenv("ICECAST_ADMIN_URL", "http://icecast:8000")
ICECAST_ADMIN_USER = os.getenv("ICECAST_ADMIN_USER", "admin")
ICECAST_ADMIN_PASSWORD = os.getenv("ICECAST_ADMIN_PASSWORD", "hackme")


async def list_mounts():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{ICECAST_ADMIN_URL}/admin/listmounts",
            auth=(ICECAST_ADMIN_USER, ICECAST_ADMIN_PASSWORD),
            params={"with_listeners": 1},
        )
        return {"status": resp.status_code, "body": resp.text}


async def kill_source(mount: str):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{ICECAST_ADMIN_URL}/admin/killsource",
            auth=(ICECAST_ADMIN_USER, ICECAST_ADMIN_PASSWORD),
            params={"mount": mount},
        )
        return {"status": resp.status_code, "body": resp.text}
