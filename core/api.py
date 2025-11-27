"""
Ouroboros System - REST API
Provides HTTP endpoints for system control and monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
import asyncio
from datetime import datetime

from .orchestrator import DynamicOrchestrator
from .verification import OracleVerificationEngine

app = FastAPI(
    title="Ouroboros System API",
    description="Autonomous Self-Healing Multi-Agent AI System",
    version="0.1.0"
)

# Global orchestrator instance
orchestrator: DynamicOrchestrator = None


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    orchestrator = DynamicOrchestrator(discovery_backend='memory')
    await orchestrator.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global orchestrator
    if orchestrator:
        await orchestrator.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Ouroboros System",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    return {
        "status": "healthy" if orchestrator.running else "stopped",
        "agents": len(orchestrator.agents),
        "running": orchestrator.running,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/agents")
async def list_agents():
    """List all agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    agents = [
        {
            "id": agent_id,
            "name": meta.name,
            "status": meta.status.value,
            "health": meta.health,
            "capabilities": list(meta.capabilities),
        }
        for agent_id, meta in orchestrator.agents.items()
    ]
    
    return {"agents": agents, "count": len(agents)}


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    meta = orchestrator.agents[agent_id]
    return {
        "id": agent_id,
        "name": meta.name,
        "status": meta.status.value,
        "health": meta.health,
        "capabilities": list(meta.capabilities),
        "dependencies": list(meta.dependencies),
        "last_beat": meta.last_beat.isoformat(),
    }


@app.post("/verify")
async def verify_system(level: int = 6):
    """Run Oracle verification"""
    try:
        engine = OracleVerificationEngine(".")
        results = await engine.verify_all(max_level=level)
        
        passed = len([r for r in results if r.status == 'pass'])
        warned = len([r for r in results if r.status == 'warn'])
        failed = len([r for r in results if r.status == 'fail'])
        
        return {
            "level": level,
            "total": len(results),
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "results": [
                {
                    "component": r.component,
                    "level": r.level,
                    "status": r.status,
                    "message": r.message,
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    # This would integrate with prometheus_client
    return {
        "agents": len(orchestrator.agents) if orchestrator else 0,
        "running": orchestrator.running if orchestrator else False,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

