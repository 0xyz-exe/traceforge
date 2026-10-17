from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

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

@app.get("/")
def root():
    return {"message": "TraceForge API", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
