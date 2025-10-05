"""API Routes for NASA Space Biology Knowledge Engine.

Provides comprehensive REST API endpoints for accessing NASA OSDR data,
knowledge graph operations, AI services, and system health monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional, Any, List
from .schemas import SearchFilters, HealthResponse, GraphResponse
from .config import settings, logger
import asyncio
import json
from datetime import datetime

router = APIRouter()

def get_services(request: Request):
    """Dependency to get services from app state."""
    return {
        'nasa_client': request.app.state.nasa_client,
        'ai_service': request.app.state.ai_service,
        'cache_service': request.app.state.cache_service,
        'graph_service': request.app.state.graph_service
    }

# ==================== NASA OSDR Data Endpoints ====================

@router.get("/datasets")
async def get_datasets(
    limit: int = Query(50, ge=1, le=200, description="Number of datasets to return"),
    page: int = Query(0, ge=0, description="Page number for pagination"),
    with_files: bool = Query(False, description="Only return datasets with public files"),
    services = Depends(get_services)
):
    """Get latest NASA space biology datasets with pagination."""
    cache_key = f"datasets:{limit}:{page}"
    
    try:
        # TEMPORARILY DISABLED CACHE - Always fetch fresh data from NASA
        # This ensures we're not returning old fallback data
        # cached = await services['cache_service'].get(cache_key)
        # if cached:
        #     logger.debug(f"Cache hit for datasets {limit}:{page}")
        #     return cached
        
        logger.info(f"Fetching fresh data from NASA OSDR (cache disabled, with_files={with_files})")
        
        # Fetch from NASA OSDR with file filtering
        data = await services['nasa_client'].get_datasets(limit=limit, page=page, with_files=with_files)
        logger.info(f"NASA client returned: {type(data)} with keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
        
        # Handle the NASA API response format
        result = {
            "data": [],
            "count": 0,
            "total": 0,
            "page": page,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
        if isinstance(data, dict) and "data" in data:
            # Our NASA client returns {"data": [...], "total": N, "count": M, "source": "..."}
            result["data"] = data["data"][:limit]
            result["count"] = data.get("count", len(result["data"]))  # Loaded count
            result["total"] = data.get("total", 0)  # Total available in OSDR
            result["source"] = data.get("source", "NASA API")
            result["message"] = data.get("message", "")
            result["error"] = data.get("error")  # Include error if present
            
            logger.info(f"Processed {result['count']} datasets from {result.get('source', 'unknown source')}")
            logger.info(f"Total available in OSDR: {result['total']}")
        else:
            logger.warning(f"Unexpected data format from NASA client: {type(data)}")
            if hasattr(data, 'get'):
                logger.warning(f"Data keys: {list(data.keys()) if hasattr(data, 'keys') else 'no keys'}")
                # Try to extract data from other possible keys
                for key in ["results", "hits", "items"]:
                    if key in data and isinstance(data[key], list):
                        result["data"] = data[key][:limit]
                        result["count"] = len(result["data"])
                        result["source"] = "NASA API (fallback)"
                        break
        
        # Cache the result
        await services['cache_service'].set(cache_key, result, ttl=settings.cache_ttl)
        
        # Build knowledge graph from the data
        if result["data"]:
            asyncio.create_task(
                services['graph_service'].build_graph_from_data(result["data"])
            )
        
        logger.info(f"Returned {len(result['data'])} datasets")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching datasets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch datasets: {str(e)}")

@router.post("/search")
async def search_studies(
    filters: SearchFilters,
    services = Depends(get_services)
):
    """Search NASA space biology studies with AI-enhanced intent parsing."""
    try:
        cache_key = f"search:{hash(str(filters.dict()))}"
        
        # Check cache first
        cached = await services['cache_service'].get(cache_key)
        if cached:
            logger.debug(f"Cache hit for search: {filters.query}")
            return cached
        
        # Parse search intent with AI if query provided
        intent = {}
        if filters.query:
            try:
                intent = await services['ai_service'].parse_intent(filters.query)
                logger.info(f"Parsed intent from '{filters.query}': {intent}")
            except Exception as e:
                logger.warning(f"Intent parsing failed: {e}")
                intent = {"original_query": filters.query, "provider": "fallback"}
        
        # Merge AI intent with filters
        search_params = {
            "query": filters.query or intent.get("query", ""),
            "page": 0,
            "size": 100
        }
        
        # Add organism filter from intent or filters
        if filters.organisms:
            search_params["organism"] = filters.organisms[0]
        elif intent.get("organisms"):
            search_params["organism"] = intent["organisms"][0]
        
        # Add mission filter
        if filters.missions:
            search_params["mission"] = filters.missions[0]
        elif intent.get("missions"):
            search_params["mission"] = intent["missions"][0]
        
        # Search NASA OSDR
        raw_results = await services['nasa_client'].search_studies(search_params)
        logger.info(f"NASA client search returned: {type(raw_results)} with keys: {raw_results.keys() if isinstance(raw_results, dict) else 'not a dict'}")
        
        # Normalize search results
        results = []
        
        if isinstance(raw_results, dict):
            if "studies" in raw_results:
                # OSDR studies format
                studies = raw_results["studies"]
                for study_id, study_info in studies.items():
                    result_item = {
                        "id": study_id,
                        "title": study_info.get("title", study_id),
                        "description": study_info.get("summary") or study_info.get("description"),
                        "organism": study_info.get("organism"),
                        "mission": study_info.get("mission"),
                        "data_types": study_info.get("data_types", []),
                        "relevance_score": 1.0  # TODO: Implement relevance scoring
                    }
                    results.append(result_item)
            
            elif "hits" in raw_results:
                # Search API hits format
                hits = raw_results["hits"]
                logger.info(f"Processing hits: {type(hits)} with {len(hits) if isinstance(hits, list) else 'not a list'} items")
                
                if isinstance(hits, list):
                    for hit in hits:
                        result_item = {
                            "id": hit.get("id") or hit.get("study_id") or hit.get("OSD_STUDY_ID"),
                            "title": hit.get("title") or hit.get("name"),
                            "description": hit.get("description") or hit.get("summary"),
                            "organism": hit.get("organism"),
                            "mission": hit.get("mission"),
                            "data_types": hit.get("data_types", []),
                            "relevance_score": hit.get("score", 1.0)
                        }
                        results.append(result_item)
                elif isinstance(hits, dict) and "hits" in hits:
                    # Nested hits structure
                    nested_hits = hits["hits"]
                    logger.info(f"Processing nested hits: {len(nested_hits) if isinstance(nested_hits, list) else 'not a list'} items")
                    for hit in nested_hits:
                        result_item = {
                            "id": hit.get("id") or hit.get("study_id") or hit.get("OSD_STUDY_ID"),
                            "title": hit.get("title") or hit.get("name"),
                            "description": hit.get("description") or hit.get("summary"),
                            "organism": hit.get("organism"),
                            "mission": hit.get("mission"),
                            "data_types": hit.get("data_types", []),
                            "relevance_score": hit.get("score", 1.0)
                        }
                        results.append(result_item)
            
            elif "results" in raw_results:
                results = raw_results["results"]
            
            elif "data" in raw_results:
                # Our NASA client format
                results = raw_results["data"]
        
        elif isinstance(raw_results, list):
            results = raw_results
        
        # If no results found, return empty (NO FALLBACK)
        if not results:
            logger.warning(f"No results found for search '{filters.query}' in NASA OSDR")
            # Return empty results - no fallback data
        
        # Sort by relevance if available
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        response = {
            "results": results,
            "count": len(results),
            "query": filters.query,
            "intent": intent,
            "search_params": search_params,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache results
        await services['cache_service'].set(cache_key, response, ttl=1800)  # 30 min cache
        
        logger.info(f"Search returned {len(results)} results for: {filters.query}")
        return response
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/study/{study_id}")
async def get_study_metadata(
    study_id: str,
    services = Depends(get_services)
):
    """Get comprehensive metadata for a specific study."""
    try:
        cache_key = f"study_meta:{study_id}"
        
        # Check cache
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
        
        # Get study details
        study_data = await services['nasa_client'].get_study_details(study_id)
        
        if "error" in study_data:
            raise HTTPException(status_code=404, detail=f"Study {study_id} not found")
        
        # Cache result
        await services['cache_service'].set(cache_key, study_data, ttl=settings.cache_ttl)
        
        return study_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get study {study_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve study: {str(e)}")

@router.get("/files/{study_ids}")
async def get_study_files(
    study_ids: str,
    page: int = Query(0, ge=0),
    size: int = Query(25, ge=1, le=100),
    all_files: bool = Query(False),
    services = Depends(get_services)
):
    """Get file listings for one or more studies."""
    try:
        cache_key = f"files:{study_ids}:{page}:{size}:{all_files}"
        
        # Check cache
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
        
        # Get files from NASA OSDR
        files_data = await services['nasa_client'].get_files(
            study_ids, page=page, size=size, all_files=all_files
        )
        
        if "error" in files_data:
            raise HTTPException(status_code=404, detail=f"Files for {study_ids} not found")
        
        # Cache result
        await services['cache_service'].set(cache_key, files_data, ttl=settings.cache_ttl)
        
        return files_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get files for {study_ids}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {str(e)}")

# ==================== Reference Data Endpoints ====================

@router.get("/organisms")
async def get_organisms(services = Depends(get_services)):
    """Get list of organisms from NASA space biology studies."""
    try:
        cache_key = "organisms:list"
        
        # Check cache
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
        
        # Fetch from NASA GEODE
        organisms_data = await services['nasa_client'].get_organisms()
        
        # Cache with long TTL since organisms don't change frequently
        await services['cache_service'].set(cache_key, organisms_data, ttl=86400)  # 24 hours
        
        return organisms_data
        
    except Exception as e:
        logger.error(f"Failed to get organisms: {e}")
        return {"organisms": [], "error": str(e)}

@router.get("/missions")
async def get_missions(services = Depends(get_services)):
    """Get list of space missions from NASA GEODE."""
    try:
        cache_key = "missions:list"
        
        # Check cache
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
        
        # Fetch from NASA GEODE
        missions_data = await services['nasa_client'].get_missions()
        
        # Cache with long TTL
        await services['cache_service'].set(cache_key, missions_data, ttl=86400)  # 24 hours
        
        return missions_data
        
    except Exception as e:
        logger.error(f"Failed to get missions: {e}")
        return {"missions": [], "error": str(e)}

@router.get("/experiments")
async def get_experiments(services = Depends(get_services)):
    """Get experiments from NASA GEODE."""
    try:
        cache_key = "experiments:list"
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
            
        data = await services['nasa_client'].get_experiments()
        await services['cache_service'].set(cache_key, data, ttl=86400)
        return data
        
    except Exception as e:
        logger.error(f"Failed to get experiments: {e}")
        return {"experiments": [], "error": str(e)}

@router.get("/payloads")
async def get_payloads(services = Depends(get_services)):
    """Get payloads from NASA GEODE."""
    try:
        cache_key = "payloads:list"
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
            
        data = await services['nasa_client'].get_payloads()
        await services['cache_service'].set(cache_key, data, ttl=86400)
        return data
        
    except Exception as e:
        logger.error(f"Failed to get payloads: {e}")
        return {"payloads": [], "error": str(e)}

@router.get("/hardware")
async def get_hardware(services = Depends(get_services)):
    """Get hardware from NASA GEODE."""
    try:
        cache_key = "hardware:list"
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
            
        data = await services['nasa_client'].get_hardware()
        await services['cache_service'].set(cache_key, data, ttl=86400)
        return data
        
    except Exception as e:
        logger.error(f"Failed to get hardware: {e}")
        return {"hardware": [], "error": str(e)}

@router.get("/vehicles")
async def get_vehicles(services = Depends(get_services)):
    """Get vehicles from NASA GEODE."""
    try:
        cache_key = "vehicles:list"
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
            
        data = await services['nasa_client'].get_vehicles()
        await services['cache_service'].set(cache_key, data, ttl=86400)
        return data
        
    except Exception as e:
        logger.error(f"Failed to get vehicles: {e}")
        return {"vehicles": [], "error": str(e)}

@router.get("/biospecimens")
async def get_biospecimens(services = Depends(get_services)):
    """Get biospecimens from NASA GEODE."""
    try:
        cache_key = "biospecimens:list"
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
            
        data = await services['nasa_client'].get_biospecimens()
        await services['cache_service'].set(cache_key, data, ttl=86400)
        return data
        
    except Exception as e:
        logger.error(f"Failed to get biospecimens: {e}")
        return {"biospecimens": [], "error": str(e)}

# ==================== Knowledge Graph Endpoints ====================

@router.get("/graph")
async def get_knowledge_graph(
    limit: int = Query(100, ge=1, le=1000),
    services = Depends(get_services)
) -> GraphResponse:
    """Get knowledge graph data for visualization."""
    try:
        cache_key = f"graph:{limit}"
        
        # Check cache
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
        
        # Get graph data
        graph_data = await services['graph_service'].get_graph(limit=limit)
        
        # Cache the result
        await services['cache_service'].set(cache_key, graph_data, ttl=3600)  # 1 hour
        
        return graph_data
        
    except Exception as e:
        logger.error(f"Failed to get graph: {e}")
        return {"nodes": [], "edges": [], "error": str(e)}

@router.get("/graph/search")
async def search_graph(
    query: str = Query(..., description="Search query for graph nodes"),
    limit: int = Query(50, ge=1, le=200),
    services = Depends(get_services)
):
    """Search the knowledge graph."""
    try:
        results = await services['graph_service'].search_graph(query, limit=limit)
        return results
        
    except Exception as e:
        logger.error(f"Graph search failed: {e}")
        return {"nodes": [], "error": str(e)}

@router.get("/graph/stats")
async def get_graph_stats(services = Depends(get_services)):
    """Get knowledge graph statistics."""
    try:
        stats = await services['graph_service'].get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        return {"error": str(e)}

# ==================== AI & Analytics Endpoints ====================

@router.post("/summarize")
async def summarize_text(
    text: str = Query(..., description="Text to summarize"),
    max_tokens: int = Query(512, ge=50, le=2000),
    services = Depends(get_services)
):
    """Generate AI summary of scientific text."""
    try:
        if len(text) < 10:
            raise HTTPException(status_code=400, detail="Text too short to summarize")
        
        summary = await services['ai_service'].summarize(text, max_tokens=max_tokens)
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.post("/insights")
async def generate_insights(
    study_ids: Optional[List[str]] = None,
    limit: int = Query(10, ge=1, le=50),
    services = Depends(get_services)
):
    """Generate AI insights from space biology data."""
    try:
        # If no study IDs provided, get recent datasets
        if not study_ids:
            datasets_response = await get_datasets(limit=limit, page=0, services=services)
            study_data = datasets_response.get("data", [])
        else:
            # Get specific studies
            study_data = []
            for study_id in study_ids:
                try:
                    study = await services['nasa_client'].get_study_details(study_id)
                    if "error" not in study:
                        study_data.append(study)
                except Exception:
                    continue
        
        # Generate insights
        insights = await services['ai_service'].generate_insights(study_data)
        return insights
        
    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        return {"insights": [], "error": str(e)}

@router.get("/timeline")
async def get_research_timeline(
    limit: int = Query(20, ge=1, le=100),
    services = Depends(get_services)
):
    """Get timeline of space biology research milestones."""
    try:
        cache_key = f"timeline:{limit}"
        
        # Check cache
        cached = await services['cache_service'].get(cache_key)
        if cached:
            return cached
        
        # Get recent datasets and extract timeline
        datasets_response = await get_datasets(limit=limit, page=0, services=services)
        datasets = datasets_response.get("data", [])
        
        timeline_events = []
        for dataset in datasets:
            if dataset.get("release_date"):
                event = {
                    "date": dataset["release_date"],
                    "title": f"Study Released: {dataset['title'][:50]}...",
                    "description": dataset.get("description", "")[:100],
                    "type": "study_release",
                    "study_id": dataset["id"]
                }
                timeline_events.append(event)
        
        # Sort by date
        timeline_events.sort(key=lambda x: x["date"], reverse=True)
        
        result = {
            "timeline_data": timeline_events,
            "count": len(timeline_events),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache result
        await services['cache_service'].set(cache_key, result, ttl=7200)  # 2 hours
        
        return result
        
    except Exception as e:
        logger.error(f"Timeline generation failed: {e}")
        return {"timeline_data": [], "error": str(e)}

# ==================== System Health & Monitoring ====================

@router.get("/health", response_model=HealthResponse)
async def get_system_health(services = Depends(get_services)):
    """Comprehensive system health check."""
    try:
        health_status = {
            "ok": True,
            "timestamp": datetime.now().isoformat(),
            "environment": settings.environment,
            "version": "1.0.0",
            "services": {},
            "degraded_services": []
        }
        
        # Check NASA OSDR API
        try:
            # Quick test of NASA API
            test_data = await services['nasa_client'].get_datasets(limit=1, page=0)
            health_status["services"]["nasa_osdr"] = {
                "status": "healthy" if test_data.get("data") else "degraded",
                "api_key_configured": bool(settings.nasa_osdr_api_key),
                "last_response_time": "< 1s"
            }
        except Exception as e:
            health_status["services"]["nasa_osdr"] = {
                "status": "unhealthy",
                "error": str(e)[:100],
                "api_key_configured": bool(settings.nasa_osdr_api_key)
            }
            health_status["degraded_services"].append("nasa_osdr")
        
        # Check AI services
        ai_status = {
            "gemini_configured": bool(settings.gemini_api_key),
            "openai_configured": bool(settings.openai_api_key),
            "status": "healthy" if (settings.gemini_api_key or settings.openai_api_key) else "degraded"
        }
        if not (settings.gemini_api_key or settings.openai_api_key):
            ai_status["fallback_mode"] = "local_processing"
            health_status["degraded_services"].append("ai_services")
        
        health_status["services"]["ai_services"] = ai_status
        
        # Check cache services
        try:
            cache_stats = await services['cache_service'].get_stats()
            health_status["services"]["cache"] = {
                "status": "healthy",
                "redis_available": cache_stats.get("redis_available", False),
                "sqlite_available": cache_stats.get("sqlite_available", True),
                "memory_available": True
            }
        except Exception as e:
            health_status["services"]["cache"] = {
                "status": "degraded",
                "error": str(e)[:100]
            }
            health_status["degraded_services"].append("cache")
        
        # Check graph services
        try:
            graph_stats = await services['graph_service'].get_stats()
            health_status["services"]["graph"] = {
                "status": "healthy",
                "neo4j_available": graph_stats.get("neo4j_available", False),
                "sqlite_available": graph_stats.get("sqlite_available", True)
            }
        except Exception as e:
            health_status["services"]["graph"] = {
                "status": "degraded",
                "error": str(e)[:100]
            }
            health_status["degraded_services"].append("graph")
        
        # Overall health determination
        if health_status["degraded_services"]:
            if "nasa_osdr" in health_status["degraded_services"]:
                health_status["ok"] = False  # NASA API is critical
            else:
                health_status["status"] = "degraded"  # Other services degraded but functional
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "ok": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
