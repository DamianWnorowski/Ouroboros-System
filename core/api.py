"""
Ouroboros System - REST API
Provides HTTP endpoints for system control and monitoring
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
import asyncio
import os
from datetime import datetime

from .orchestrator import DynamicOrchestrator
from .verification import OracleVerificationEngine
from .auth import require_auth, rate_limit, get_auth_manager, AuthenticationError
from .validation import (
    VerifyRequest, AgentCreateRequest, AgentUpdateRequest,
    PaginationParams, FilterParams, ErrorResponse
)

app = FastAPI(
    title="Ouroboros System API",
    description="Autonomous Self-Healing Multi-Agent AI System",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
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
@rate_limit(max_requests=1000, window=60)
async def root():
    """Root endpoint"""
    return {
        "name": "Ouroboros System",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
@rate_limit(max_requests=1000, window=60)
async def health():
    """Health check endpoint (public, no auth required)"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    return {
        "status": "healthy" if orchestrator.running else "stopped",
        "agents": len(orchestrator.agents),
        "running": orchestrator.running,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/agents")
@rate_limit(max_requests=100, window=60)
@require_auth(roles=['user', 'admin'])
async def list_agents(
    request: Request,
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends()
):
    """List all agents with pagination and filtering"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Get all agents
    all_agents = [
        {
            "id": agent_id,
            "name": meta.name,
            "status": meta.status.value,
            "health": meta.health,
            "capabilities": list(meta.capabilities),
        }
        for agent_id, meta in orchestrator.agents.items()
    ]
    
    # Apply filters
    if filters.status:
        all_agents = [a for a in all_agents if a['status'] == filters.status]
    if filters.capability:
        all_agents = [a for a in all_agents if filters.capability in a['capabilities']]
    if filters.search:
        search_lower = filters.search.lower()
        all_agents = [
            a for a in all_agents
            if search_lower in a['name'].lower() or search_lower in a['id'].lower()
        ]
    
    # Apply pagination
    total = len(all_agents)
    paginated_agents = all_agents[pagination.offset:pagination.offset + pagination.limit]
    
    return {
        "agents": paginated_agents,
        "count": len(paginated_agents),
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "pages": (total + pagination.page_size - 1) // pagination.page_size
    }


@app.get("/agents/{agent_id}")
@rate_limit(max_requests=100, window=60)
@require_auth(roles=['user', 'admin'])
async def get_agent(agent_id: str, request: Request):
    """Get agent details"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Validate agent_id to prevent injection
    if not agent_id or len(agent_id) > 100:
        raise HTTPException(status_code=400, detail="Invalid agent ID")
    
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
@rate_limit(max_requests=10, window=60)  # Lower limit for expensive operation
@require_auth(roles=['user', 'admin'])
async def verify_system(request: Request, verify_req: VerifyRequest):
    """Run Oracle verification with input validation"""
    try:
        # Validate level
        level = max(0, min(6, verify_req.level))
        
        # Use provided path or default
        base_path = verify_req.path or "."
        
        engine = OracleVerificationEngine(base_path)
        results = await engine.verify_all(max_level=level)
        
        passed = len([r for r in results if r.status == 'pass'])
        warned = len([r for r in results if r.status == 'warn'])
        failed = len([r for r in results if r.status == 'fail'])
        
        response = {
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
        
        if verify_req.export_json:
            # In production, save to file or return as downloadable
            response["export_url"] = f"/verify/export/{datetime.utcnow().timestamp()}"
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/metrics")
@rate_limit(max_requests=100, window=60)
@require_auth(roles=['admin', 'monitoring'])  # Metrics typically require admin
async def get_metrics(request: Request):
    """Get Prometheus metrics"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # This would integrate with prometheus_client
    return {
        "agents": len(orchestrator.agents),
        "running": orchestrator.running,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/auth/login")
@rate_limit(max_requests=10, window=60)  # Lower limit for login
async def login(request: Request, username: str, password: str):
    """Login endpoint (simplified - use proper user management in production)"""
    # In production, verify against user database
    # For now, simple check (REPLACE WITH PROPER AUTH)
    if username == os.getenv('ADMIN_USER', 'admin') and password == os.getenv('ADMIN_PASSWORD', 'change-me'):
        auth_manager = get_auth_manager()
        token = auth_manager.create_token(user_id=username, roles=['admin'])
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise AuthenticationError("Invalid credentials")


@app.exception_handler(AuthenticationError)
async def auth_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": "AUTH_ERROR"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP errors with proper format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": f"HTTP_{exc.status_code}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

