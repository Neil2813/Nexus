"""Pydantic schemas for NASA Space Biology Knowledge Engine API.

Defines request/response models for type safety and API documentation.
"""

from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict, Union
from datetime import datetime

class Dataset(BaseModel):
    """NASA space biology dataset model."""
    id: str = Field(..., description="Unique dataset identifier")
    title: Optional[str] = Field(None, description="Dataset title")
    description: Optional[str] = Field(None, description="Dataset description")
    organism: Optional[str] = Field(None, description="Primary organism studied")
    mission: Optional[str] = Field(None, description="Space mission")
    release_date: Optional[str] = Field(None, description="Data release date")
    data_types: Optional[List[str]] = Field(default_factory=list, description="Types of data collected")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw API response data")

class SearchFilters(BaseModel):
    """Search filters for NASA space biology studies."""
    query: Optional[str] = Field("", description="Natural language search query")
    organisms: Optional[List[str]] = Field(default_factory=list, description="Filter by organisms")
    missions: Optional[List[str]] = Field(default_factory=list, description="Filter by missions")
    data_types: Optional[List[str]] = Field(default_factory=list, description="Filter by data types")

class GraphNode(BaseModel):
    """Knowledge graph node model."""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node display label")
    type: str = Field(..., description="Node type (study, organism, mission, etc.)")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional node properties")

class GraphEdge(BaseModel):
    """Knowledge graph edge model."""
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Relationship type")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional edge properties")

class GraphResponse(BaseModel):
    """Knowledge graph response model."""
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
    node_count: Optional[int] = Field(None, description="Total number of nodes")
    edge_count: Optional[int] = Field(None, description="Total number of edges")
    provider: Optional[str] = Field(None, description="Data provider (neo4j, sqlite, etc.)")
    error: Optional[str] = Field(None, description="Error message if applicable")

class SearchResult(BaseModel):
    """Search result item model."""
    id: str = Field(..., description="Study identifier")
    title: Optional[str] = Field(None, description="Study title")
    description: Optional[str] = Field(None, description="Study description")
    organism: Optional[str] = Field(None, description="Primary organism")
    mission: Optional[str] = Field(None, description="Space mission")
    data_types: Optional[List[str]] = Field(default_factory=list, description="Data types")
    relevance_score: Optional[float] = Field(None, description="Search relevance score")

class SearchResponse(BaseModel):
    """Search response model."""
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    count: int = Field(0, description="Number of results returned")
    query: Optional[str] = Field(None, description="Original search query")
    intent: Optional[Dict[str, Any]] = Field(None, description="Parsed search intent")
    search_params: Optional[Dict[str, Any]] = Field(None, description="Final search parameters used")
    timestamp: Optional[str] = Field(None, description="Response timestamp")

class AIServiceStatus(BaseModel):
    """AI service status model."""
    gemini_configured: bool = Field(False, description="Gemini API configured")
    openai_configured: bool = Field(False, description="OpenAI API configured")
    status: str = Field(..., description="Service status")
    fallback_mode: Optional[str] = Field(None, description="Fallback mode if applicable")

class ServiceStatus(BaseModel):
    """Generic service status model."""
    status: str = Field(..., description="Service status (healthy, degraded, unhealthy)")
    api_key_configured: Optional[bool] = Field(None, description="API key configured")
    last_response_time: Optional[str] = Field(None, description="Last response time")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    redis_available: Optional[bool] = Field(None, description="Redis availability")
    sqlite_available: Optional[bool] = Field(None, description="SQLite availability")
    memory_available: Optional[bool] = Field(None, description="Memory cache availability")
    neo4j_available: Optional[bool] = Field(None, description="Neo4j availability")

class HealthResponse(BaseModel):
    """System health response model."""
    ok: bool = Field(..., description="Overall system health")
    timestamp: str = Field(..., description="Health check timestamp")
    environment: str = Field(..., description="Environment (development, production)")
    version: str = Field(..., description="Application version")
    services: Dict[str, Union[ServiceStatus, AIServiceStatus, Dict[str, Any]]] = Field(
        default_factory=dict, 
        description="Individual service statuses"
    )
    degraded_services: List[str] = Field(default_factory=list, description="List of degraded services")
    status: Optional[str] = Field(None, description="Overall status if degraded")
    error: Optional[str] = Field(None, description="Error message if system unhealthy")

class SummaryResponse(BaseModel):
    """AI summary response model."""
    summary: str = Field(..., description="Generated summary text")
    provider: str = Field(..., description="AI provider used (gemini, openai, local_fallback)")
    model: Optional[str] = Field(None, description="Specific model used")
    note: Optional[str] = Field(None, description="Additional notes about the summarization")
    error: Optional[str] = Field(None, description="Error message if applicable")

class InsightsResponse(BaseModel):
    """AI insights response model."""
    insights: List[str] = Field(default_factory=list, description="Generated insights")
    provider: str = Field(..., description="Provider used for insights generation")
    model: Optional[str] = Field(None, description="Specific model used")
    note: Optional[str] = Field(None, description="Additional notes")
    error: Optional[str] = Field(None, description="Error message if applicable")

class TimelineEvent(BaseModel):
    """Timeline event model."""
    date: str = Field(..., description="Event date")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    type: str = Field(..., description="Event type")
    study_id: Optional[str] = Field(None, description="Associated study ID")

class TimelineResponse(BaseModel):
    """Timeline response model."""
    timeline_data: List[TimelineEvent] = Field(default_factory=list, description="Timeline events")
    count: int = Field(0, description="Number of events")
    timestamp: str = Field(..., description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if applicable")

class DatasetResponse(BaseModel):
    """Dataset listing response model."""
    data: List[Dataset] = Field(default_factory=list, description="Dataset list")
    total: int = Field(0, description="Total available datasets")
    page: int = Field(0, description="Current page number")
    limit: int = Field(50, description="Results per page")
    count: int = Field(0, description="Number of results in this response")
    timestamp: str = Field(..., description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if applicable")
