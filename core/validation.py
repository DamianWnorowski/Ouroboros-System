"""
Ouroboros System - Input Validation
Pydantic models for request validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class VerificationLevel(int, Enum):
    """Verification level enum"""
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6


class VerifyRequest(BaseModel):
    """Request model for verification endpoint"""
    level: int = Field(default=6, ge=0, le=6, description="Verification level (0-6)")
    path: Optional[str] = Field(default=None, max_length=4096, description="Path to verify")
    export_json: bool = Field(default=False, description="Export results as JSON")
    
    @validator('path')
    def validate_path(cls, v):
        """Validate path to prevent path traversal"""
        if v is None:
            return v
        
        # Prevent path traversal
        if '..' in v or v.startswith('/'):
            raise ValueError("Invalid path: path traversal not allowed")
        
        # Prevent absolute paths
        import os
        if os.path.isabs(v):
            raise ValueError("Invalid path: absolute paths not allowed")
        
        return v


class AgentCreateRequest(BaseModel):
    """Request model for creating an agent"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    dependencies: List[str] = Field(default_factory=list, description="Agent dependencies")
    auto_heal: bool = Field(default=True, description="Enable auto-healing")


class AgentUpdateRequest(BaseModel):
    """Request model for updating an agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    capabilities: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    auto_heal: Optional[bool] = None


class GeneratorDNARequest(BaseModel):
    """Request model for generator DNA"""
    id: str = Field(..., min_length=1, max_length=100, regex=r'^[a-z][a-z0-9-]*$')
    name: str = Field(..., min_length=1, max_length=200)
    system: str = Field(..., min_length=1, max_length=100)
    codename: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=1000)
    version: str = Field(..., regex=r'^\d+\.\d+\.\d+$')
    category: str = Field(..., regex=r'^(infrastructure|sdk|documentation|testing|monitoring|deployment)$')
    outputs: List[Dict[str, Any]] = Field(default_factory=list)
    templates: List[Dict[str, Any]] = Field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit"""
        return self.page_size


class FilterParams(BaseModel):
    """Filter parameters"""
    status: Optional[str] = None
    capability: Optional[str] = None
    search: Optional[str] = Field(None, max_length=100)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

