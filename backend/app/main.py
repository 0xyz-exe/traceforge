from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import auth, services, ingest, metrics, logs, traces

app = FastAPI(
    title="TraceForge API",
    version="0.1.0",
    description="Developer observability platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth")
app.include_router(services.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(traces.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "TraceForge API", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
