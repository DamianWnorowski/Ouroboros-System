# Ouroboros System - API Reference

## REST API Endpoints

Base URL: `http://localhost:8000`

### Health & Status

#### `GET /`
Root endpoint - System information

**Response:**
```json
{
  "name": "Ouroboros System",
  "version": "0.1.0",
  "status": "running",
  "timestamp": "2024-12-XX..."
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "agents": 5,
  "running": true,
  "timestamp": "2024-12-XX..."
}
```

### Agent Management

#### `GET /agents`
List all agents

**Response:**
```json
{
  "agents": [
    {
      "id": "agent-1",
      "name": "Example Agent",
      "status": "active",
      "health": 1.0,
      "capabilities": ["example", "demo"]
    }
  ],
  "count": 1
}
```

#### `GET /agents/{agent_id}`
Get agent details

**Response:**
```json
{
  "id": "agent-1",
  "name": "Example Agent",
  "status": "active",
  "health": 1.0,
  "capabilities": ["example"],
  "dependencies": [],
  "last_beat": "2024-12-XX..."
}
```

### Verification

#### `POST /verify`
Run Oracle verification

**Parameters:**
- `level` (query, optional): Verification level (0-6, default: 6)

**Response:**
```json
{
  "level": 6,
  "total": 25,
  "passed": 23,
  "warned": 1,
  "failed": 1,
  "results": [...]
}
```

### Metrics

#### `GET /metrics`
Prometheus metrics endpoint

**Response:** Prometheus format

---

## Usage Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### List Agents
```bash
curl http://localhost:8000/agents
```

### Run Verification
```bash
curl -X POST "http://localhost:8000/verify?level=3"
```

### Get Agent Details
```bash
curl http://localhost:8000/agents/agent-1
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Agent agent-1 not found"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Orchestrator not initialized"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message"
}
```

---

*API Reference - Complete endpoint documentation*

