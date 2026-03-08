from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, config, mounts, runtime, logs, nginx_control, listener_auth, sockets, relays, listeners
from routers import auth, config, mounts, runtime, logs, nginx_control, listener_auth
from routers import auth, config, mounts, runtime, logs

app = FastAPI(title="Icecast Control Center API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(mounts.router, prefix="/api/mounts", tags=["mounts"])
app.include_router(runtime.router, prefix="/api/runtime", tags=["runtime"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(nginx_control.router, prefix="/api/nginx", tags=["nginx"])
app.include_router(listener_auth.router, prefix="/api/listener-auth", tags=["listener-auth"])
app.include_router(sockets.router, prefix="/api/sockets", tags=["sockets"])
app.include_router(relays.router, prefix="/api/relays", tags=["relays"])
app.include_router(listeners.router, prefix="/api/listeners", tags=["listeners"])
