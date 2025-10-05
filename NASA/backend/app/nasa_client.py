"""NASA OSDR API client with comprehensive endpoint support.

Provides access to all NASA Open Science Data Repository (OSDR) endpoints
with proper authentication, error handling, and graceful fallbacks.
"""

import httpx
from typing import Optional, Any, Dict, List
from .config import settings, logger
import json

class NASAClient:
    """Client for interacting with NASA OSDR and GEODE APIs."""
    
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.osdr_base = settings.nasa_osdr_base_url.rstrip("/")
        self.geode_base = settings.nasa_geode_base_url.rstrip("/")
        self.api_base = settings.nasa_api_base_url.rstrip("/")
        self.genelab_base = settings.nasa_genelab_base_url.rstrip("/")
        self.api_key = settings.nasa_osdr_api_key
        
        # Create HTTP client with proper headers
        headers = {
            "User-Agent": "NEXUS-NASA-Space-Biology-Knowledge-Engine/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Add API key to headers if available (NASA APIs use different auth methods)
        if self.api_key:
            # Try multiple authentication methods
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Some NASA APIs use api_key as query parameter
            self.api_key_param = {"api_key": self.api_key}
        else:
            self.api_key_param = {}
        
        self.client = client or httpx.AsyncClient(
            timeout=30.0,
            headers=headers,
            follow_redirects=True
        )
        
        logger.info(f"NASA Client initialized:")
        logger.info(f"  - OSDR Base: {self.osdr_base}")
        logger.info(f"  - GEODE Base: {self.geode_base}")
        logger.info(f"  - API Base: {self.api_base}")
        logger.info(f"  - GeneLab Base: {self.genelab_base}")
        logger.info(f"  - API Key: {'✓' if self.api_key else '✗'}")

    async def get_datasets(self, limit: int = 50, page: int = 0, with_files: bool = False) -> Dict[str, Any]:
        """Get latest studies/datasets from OSDR with pagination."""
        # NASA OSDR Bio Repo API - Returns genuine space biology studies with complete data
        endpoints_to_try = [
            # Endpoint 1: Bio Repo Search with data sources (PRIMARY - has everything)
            {
                "url": f"{self.osdr_base}/bio/repo/search",
                "params": {
                    "q": "",
                    "data_source": "cgene,alsda,esa",
                    "data_type": "study",
                    "size": min(limit * 10, 500),  # Fetch 10x more to filter for genuine studies
                    "from": page * limit
                }
            },
            # Endpoint 2: OSDR data search with data sources (FALLBACK)
            {
                "url": f"{self.osdr_base}/osdr/data/search",
                "params": {
                    "size": min(limit * 10, 500),  # Fetch 10x more to filter
                    "from": page * limit,
                    "data_source": "cgene,alsda"
                }
            },
            # Endpoint 3: OSDR general search (LAST RESORT - fetch even more to filter)
            {
                "url": f"{self.osdr_base}/osdr/data/search",
                "params": {
                    "size": min(limit * 10, 500),  # Fetch 10x more to filter
                    "from": page * limit
                }
            }
        ]
        
        logger.info(f"=" * 80)
        logger.info(f"ATTEMPTING NASA OSDR API CALL")
        logger.info(f"Trying {len(endpoints_to_try)} endpoint variations")
        logger.info(f"API Key configured: {bool(self.api_key)}")
        logger.info(f"=" * 80)
        
        for idx, endpoint_config in enumerate(endpoints_to_try):
            url = endpoint_config["url"]
            params = endpoint_config["params"]
            
            logger.info(f"\nAttempt {idx + 1}/{len(endpoints_to_try)}:")
            logger.info(f"  URL: {url}")
            logger.info(f"  Params: {params}")
            
            try:
                # Make request with proper timeout
                response = await self.client.get(url, params=params, timeout=30.0)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except Exception as json_error:
                        logger.warning(f"  ❌ JSON parse error: {json_error}")
                        logger.warning(f"  Response text: {response.text[:200]}")
                        continue
                    
                    logger.info(f"  ✅ Status 200 - Success!")
                    logger.info(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                    
                    # Skip if empty response
                    if not data or (isinstance(data, dict) and not data.keys()):
                        logger.warning(f"  ❌ Empty response, trying next endpoint...")
                        continue
                    
                    datasets = []
                    
                    # OSDR Elasticsearch format (primary format)
                    if 'hits' in data and isinstance(data['hits'], dict):
                        hits_data = data['hits']
                        # Total can be either an integer or a dict with 'value' key
                        total_raw = hits_data.get('total', 0)
                        if isinstance(total_raw, dict):
                            total = total_raw.get('value', 0)
                        else:
                            total = total_raw
                        
                        if 'hits' in hits_data and isinstance(hits_data['hits'], list):
                            hits = hits_data['hits']
                            logger.info(f"  ✅ Found {len(hits)} hits out of {total:,} total in OSDR!")
                            
                            for hit in hits:
                                dataset = self._transform_osdr_hit_to_dataset(hit)
                                if dataset:
                                    # Use _id as fallback if no Study Identifier
                                    if not dataset.get('id') or dataset.get('id') == 'unknown':
                                        dataset['id'] = hit.get('_id', f"OSDR-{len(datasets)}")
                                    
                                    # FILTER: Only include genuine NASA space biology studies
                                    dataset_id = dataset.get('id', '')
                                    if dataset_id.startswith('OSD-') or dataset_id.startswith('GLDS-') or dataset_id.startswith('GLDS_'):
                                        datasets.append(dataset)
                                        logger.info(f"     ✅ {dataset.get('id')}: {dataset.get('title', 'No title')[:60]}")
                                    else:
                                        logger.debug(f"     ⏭️  Skipped non-NASA study: {dataset_id}")
                                else:
                                    logger.warning(f"     ❌ Skipped null dataset from hit: {hit.get('_id', 'unknown')}")
                    
                    elif 'hits' in data and isinstance(data['hits'], list):
                        hits = data['hits']
                        logger.info(f"  ✅ Found {len(hits)} hits in direct list format")
                        
                        for hit in hits:
                            dataset = self._transform_hit_to_dataset(hit)
                            if dataset and dataset.get('id'):
                                # FILTER: Only genuine NASA studies
                                dataset_id = dataset.get('id', '')
                                if dataset_id.startswith('OSD-') or dataset_id.startswith('GLDS-') or dataset_id.startswith('GLDS_'):
                                    datasets.append(dataset)
                    
                    # Visualization API format (direct list of studies)
                    elif isinstance(data, list):
                        logger.info(f"  ✅ Found {len(data)} studies in direct list format (Visualization API)")
                        for study in data:
                            dataset = self._transform_visualization_study(study)
                            if dataset and dataset.get('id'):
                                # FILTER: Only genuine NASA studies
                                dataset_id = dataset.get('id', '')
                                if dataset_id.startswith('OSD-') or dataset_id.startswith('GLDS-') or dataset_id.startswith('GLDS_'):
                                    datasets.append(dataset)
                    
                    # Studies key format
                    elif 'studies' in data and isinstance(data['studies'], list):
                        studies = data['studies']
                        logger.info(f"  ✅ Found {len(studies)} studies in 'studies' key")
                        for study in studies:
                            dataset = self._transform_visualization_study(study)
                            if dataset and dataset.get('id'):
                                # FILTER: Only genuine NASA studies
                                dataset_id = dataset.get('id', '')
                                if dataset_id.startswith('OSD-') or dataset_id.startswith('GLDS-') or dataset_id.startswith('GLDS_'):
                                    datasets.append(dataset)
                    
                    # Check if we got meaningful data
                    if datasets and len(datasets) > 0:
                        # Get total from the response
                        hits_data = data.get('hits', {})
                        if isinstance(hits_data, dict):
                            total_raw = hits_data.get('total', len(datasets))
                            if isinstance(total_raw, dict):
                                total = total_raw.get('value', len(datasets))
                            else:
                                total = total_raw
                        else:
                            total = len(datasets)
                        
                        # File filtering disabled - most NASA studies don't have public files via API
                        # Users can check files on individual dataset pages
                        if with_files:
                            logger.warning(f"  ⚠️  File filtering requested but disabled (most studies have no API-accessible files)")
                            # Don't filter - just return all datasets
                        
                        logger.info(f"  ✅ SUCCESS! Fetched {len(datasets)} datasets from NASA OSDR")
                        logger.info(f"  📊 Total available in OSDR: {total:,}")
                        return {
                            "data": datasets,
                            "total": total,
                            "count": len(datasets),
                            "page": page,
                            "size": limit,
                            "source": "NASA OSDR API",
                            "message": f"Fetched {len(datasets)} of {total:,} datasets from NASA Open Science Data Repository",
                            "filtered_for_files": with_files
                        }
                    else:
                        logger.warning(f"  ⚠️  Endpoint {idx + 1} returned empty data, trying next...")
                        continue  # Try next endpoint
                else:
                    logger.warning(f"  ❌ Status {response.status_code}, trying next endpoint...")
                    continue  # Try next endpoint
                    
            except Exception as endpoint_error:
                logger.warning(f"  ❌ Endpoint {idx + 1} failed: {endpoint_error}")
                continue  # Try next endpoint
        
        # If all endpoints failed, return error (NO FALLBACK)
        logger.error(f"=" * 80)
        logger.error(f"ALL NASA OSDR API ENDPOINTS FAILED")
        logger.error(f"Cannot fetch datasets - NASA API is unavailable")
        logger.error(f"=" * 80)
        
        # Return error response instead of fallback
        return {
            "data": [],
            "total": 0,
            "count": 0,
            "page": page,
            "size": limit,
            "source": "Error",
            "error": "NASA OSDR API is currently unavailable. Please check your internet connection and try again.",
            "message": "Failed to fetch datasets from NASA OSDR API"
        }

    def _transform_hit_to_dataset(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """Transform API hit to standardized dataset format."""
        return {
            "id": hit.get('id') or hit.get('OSD_STUDY_ID') or hit.get('study_id', 'unknown'),
            "title": hit.get('title') or hit.get('name') or hit.get('study_title', 'Untitled Study'),
            "description": hit.get('description') or hit.get('summary') or hit.get('abstract', ''),
            "organism": hit.get('organism') or hit.get('organism_name') or hit.get('species'),
            "mission": hit.get('mission') or hit.get('mission_name') or hit.get('flight'),
            "data_types": hit.get('data_types', []) or hit.get('data_type', []),
            "release_date": hit.get('release_date') or hit.get('created_date') or hit.get('date'),
            "study_type": hit.get('study_type', 'Unknown'),
            "publications": hit.get('publication_count', 0) or hit.get('publications', 0),
            "samples": hit.get('sample_count', 0) or hit.get('samples', 0)
        }
    
    def _transform_study_to_dataset(self, study_id: str, study_info: Dict[str, Any]) -> Dict[str, Any]:
        """Transform study object to standardized dataset format."""
        return {
            "id": study_id,
            "title": study_info.get('title') or study_info.get('name', study_id),
            "description": study_info.get('description') or study_info.get('summary', ''),
            "organism": study_info.get('organism') or study_info.get('species'),
            "mission": study_info.get('mission') or study_info.get('flight'),
            "data_types": study_info.get('data_types', []),
            "release_date": study_info.get('release_date') or study_info.get('date'),
            "study_type": study_info.get('study_type', 'Unknown'),
            "publications": study_info.get('publication_count', 0),
            "samples": study_info.get('sample_count', 0)
        }
    
    def _transform_visualization_study(self, study: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Visualization API study to standardized dataset format."""
        return {
            "id": study.get('accession') or study.get('study_id') or study.get('id', 'unknown'),
            "title": study.get('title') or study.get('study_title', 'Untitled Study'),
            "description": study.get('description') or study.get('study_description', ''),
            "organism": study.get('organism') or (study.get('organisms', [None])[0] if isinstance(study.get('organisms'), list) else None),
            "mission": study.get('mission') or study.get('flight_program'),
            "data_types": study.get('assay_types', []) or study.get('data_types', []),
            "release_date": study.get('release_date') or study.get('public_release_date'),
            "study_type": study.get('study_type') or study.get('project_type', 'Space Biology'),
            "publications": len(study.get('publications', [])) if isinstance(study.get('publications'), list) else 0,
            "samples": study.get('sample_count', 0),
            "has_files": study.get('has_files', False),
            "file_count": study.get('file_count', 0)
        }
    
    def _transform_apod_to_dataset(self, apod_item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform APOD (Astronomy Picture of the Day) item to dataset format."""
        return {
            "id": f"APOD-{apod_item.get('date', 'unknown')}",
            "title": apod_item.get('title', 'Astronomy Picture of the Day'),
            "description": apod_item.get('explanation', ''),
            "organism": "Space Environment",
            "mission": "APOD",
            "data_types": ["Image", "Astronomy"],
            "release_date": apod_item.get('date'),
            "study_type": "Astronomy",
            "publications": 0,
            "samples": 1,
            "image_url": apod_item.get('url'),
            "hd_image_url": apod_item.get('hdurl')
        }
    
    def _transform_mars_weather_to_dataset(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Mars weather data to dataset format."""
        return {
            "id": f"Mars-Weather-{weather_data.get('sol_keys', [0])[0] if weather_data.get('sol_keys') else 'unknown'}",
            "title": "Mars Weather Data",
            "description": f"Mars weather observations from Sol {weather_data.get('sol_keys', [0])[0] if weather_data.get('sol_keys') else 'unknown'}",
            "organism": "Mars Environment",
            "mission": "InSight",
            "data_types": ["Weather", "Atmospheric"],
            "release_date": weather_data.get('sol_keys', [0])[0] if weather_data.get('sol_keys') else None,
            "study_type": "Planetary Science",
            "publications": 0,
            "samples": len(weather_data.get('sol_keys', []))
        }
    
    def _transform_neo_to_dataset(self, neo_object: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Near Earth Object data to dataset format."""
        return {
            "id": f"NEO-{neo_object.get('id', 'unknown')}",
            "title": f"Near Earth Object: {neo_object.get('name', 'Unknown')}",
            "description": f"Asteroid {neo_object.get('name', 'Unknown')} - {neo_object.get('designation', '')}",
            "organism": "Space Environment",
            "mission": "NEO Program",
            "data_types": ["Orbital", "Physical"],
            "release_date": neo_object.get('close_approach_data', [{}])[0].get('close_approach_date') if neo_object.get('close_approach_data') else None,
            "study_type": "Planetary Defense",
            "publications": 0,
            "samples": 1,
            "diameter": neo_object.get('estimated_diameter', {}).get('meters', {}).get('estimated_diameter_max')
        }
    
    def _transform_earth_assets_to_dataset(self, earth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Earth assets data to dataset format."""
        return {
            "id": f"Earth-{earth_data.get('id', 'unknown')}",
            "title": "Earth Observation",
            "description": f"Earth observation data from {earth_data.get('date', 'unknown date')}",
            "organism": "Earth Environment",
            "mission": "Earth Observatory",
            "data_types": ["Satellite", "Imagery"],
            "release_date": earth_data.get('date'),
            "study_type": "Earth Science",
            "publications": 0,
            "samples": 1,
            "image_url": earth_data.get('url')
        }
    
    def _transform_patent_to_dataset(self, patent: Dict[str, Any]) -> Dict[str, Any]:
        """Transform NASA tech transfer patent to dataset format."""
        return {
            "id": f"Patent-{patent.get('id', 'unknown')}",
            "title": patent.get('title', 'NASA Technology Patent'),
            "description": patent.get('abstract', ''),
            "organism": "Technology",
            "mission": "Tech Transfer",
            "data_types": ["Patent", "Technology"],
            "release_date": patent.get('date'),
            "study_type": "Technology Transfer",
            "publications": 1,
            "samples": 1,
            "patent_number": patent.get('patent_number')
        }

    def _transform_osdr_hit_to_dataset(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        """Transform OSDR Elasticsearch hit to dataset format."""
        source = hit.get('_source', {})
        
        # Extract key information from OSDR data
        title = source.get('Study Title', source.get('Project Title', 'OSDR Study'))
        description = source.get('Study Description', source.get('Project Description', ''))
        organism = source.get('organism', source.get('Material Type', 'Unknown'))
        mission = source.get('Mission', {})
        mission_name = mission.get('Name', 'Unknown Mission') if isinstance(mission, dict) else str(mission)
        
        # Extract dates
        release_date = source.get('Study Public Release Date', source.get('Project Release Date'))
        if not release_date and mission and isinstance(mission, dict):
            release_date = mission.get('Start Date', mission.get('End Date'))
        
        # Extract data types
        data_types = []
        if source.get('Study Assay Technology Type'):
            data_types.append(source['Study Assay Technology Type'])
        if source.get('Study Assay Technology Platform'):
            data_types.append(source['Study Assay Technology Platform'])
        if source.get('Study Assay Measurement Type'):
            data_types.append(source['Study Assay Measurement Type'])
        if not data_types:
            data_types = ['Biological', 'Space Research']
        
        return {
            "id": source.get('Study Identifier', source.get('Project Identifier', hit.get('_id', 'unknown'))),
            "title": title,
            "description": description,
            "organism": organism,
            "mission": mission_name,
            "data_types": data_types,
            "release_date": release_date,
            "study_type": source.get('Study Protocol Type', 'Space Biology'),
            "publications": 1 if source.get('Study Publication Title') else 0,
            "samples": 1,
            "flight_program": source.get('Flight Program'),
            "space_program": source.get('Space Program'),
            "managing_center": source.get('Managing NASA Center'),
            "funding_agency": source.get('Study Funding Agency'),
            "accession": source.get('Accession'),
            "data_source_url": source.get('Authoritative Source URL')
        }

    async def search_studies(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search studies using OSDR search API with flexible filtering."""
        try:
            # Try OSDR search endpoints with correct parameters
            search_endpoints = [
                # OSDR Search API - Primary search endpoint (working!)
                {
                    "url": f"{self.osdr_base}/osdr/data/search",
                    "params": {"format": "json"}
                },
                # OSDR Search API - With query parameter
                {
                    "url": f"{self.osdr_base}/osdr/data/search",
                    "params": {
                        "format": "json",
                        "q": filters.get("query", "")
                    }
                },
                # OSDR Search API - With API key
                {
                    "url": f"{self.osdr_base}/osdr/data/search",
                    "params": {
                        "format": "json",
                        "q": filters.get("query", ""),
                        **self.api_key_param
                    }
                },
                # OSDR Search API - Biology specific
                {
                    "url": f"{self.osdr_base}/osdr/data/search",
                    "params": {
                        "format": "json",
                        "q": f"biology {filters.get('query', '')}"
                    }
                },
                # OSDR Search API - Space biology specific
                {
                    "url": f"{self.osdr_base}/osdr/data/search",
                    "params": {
                        "format": "json",
                        "q": f"space biology {filters.get('query', '')}"
                    }
                }
            ]
            
            for i, endpoint in enumerate(search_endpoints):
                try:
                    params = endpoint["params"].copy()
                    
                    # Add search parameters
                    if "query" in filters and filters["query"]:
                        params["q"] = filters["query"]
                        params["query"] = filters["query"]
                    if "page" in filters:
                        params["from"] = filters["page"] * filters.get("size", 25)
                        params["offset"] = filters["page"] * filters.get("size", 25)
                    if "size" in filters:
                        params["size"] = filters["size"]
                        params["limit"] = filters["size"]
                    if "organism" in filters:
                        params["organism"] = filters["organism"]
                    if "mission" in filters:
                        params["mission"] = filters["mission"]
                    
                    logger.info(f"Searching with endpoint {i+1}: {endpoint['url']} with params: {params}")
                    response = await self.client.get(endpoint['url'], params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"Search endpoint {i+1} returned status 200")
                        
                        # Try to extract results from different formats
                        results = []
                        
                        # OSDR Elasticsearch format
                        if 'hits' in data and isinstance(data['hits'], dict):
                            hits_data = data['hits']
                            if 'hits' in hits_data and isinstance(hits_data['hits'], list):
                                osdr_hits = hits_data['hits']
                                logger.info(f"Found {len(osdr_hits)} OSDR search results")
                                results = [self._transform_osdr_hit_to_dataset(hit) for hit in osdr_hits]
                        elif 'hits' in data and isinstance(data['hits'], list):
                            results = data['hits']
                        elif 'studies' in data and isinstance(data['studies'], dict):
                            studies = data['studies']
                            results = [{"id": sid, **info} for sid, info in studies.items()]
                        elif 'results' in data and isinstance(data['results'], list):
                            results = data['results']
                        elif isinstance(data, list):
                            results = data
                        
                        if results and len(results) > 0:
                            logger.info(f"Search endpoint {i+1} returned {len(results)} results")
                            return {
                                "hits": results,
                                "total": data.get('total', data.get('total_hits', len(results))),
                                "source": f"NASA Search API Endpoint {i+1}",
                                "message": f"Found {len(results)} results from NASA search"
                            }
                        else:
                            logger.warning(f"Search endpoint {i+1} returned empty results, trying next")
                            continue
                    else:
                        logger.warning(f"Search endpoint {i+1} returned status {response.status_code}")
                        continue
                        
                except Exception as endpoint_error:
                    logger.warning(f"Search endpoint {i+1} failed: {endpoint_error}")
                    continue
            
            # If all search endpoints failed, return error (NO FALLBACK)
            raise Exception("All NASA search endpoints failed")
            
        except Exception as e:
            logger.error(f"Search studies failed: {e}")
            
            # Return error response (NO FALLBACK)
            return {
                "hits": [],
                "total": 0,
                "source": "Error",
                "error": f"NASA search API unavailable: {str(e)}",
                "message": "Failed to search NASA OSDR. Please try again."
            }

    async def get_organisms(self) -> Dict[str, Any]:
        """Get list of organisms from actual NASA OSDR datasets."""
        logger.info("Fetching organisms from NASA OSDR datasets")
        
        try:
            # Fetch datasets to extract organisms
            datasets_response = await self.get_datasets(limit=100, page=0)
            datasets = datasets_response.get('data', [])
            
            # Extract unique organisms from datasets
            organisms_set = set()
            organism_counts = {}
            
            for dataset in datasets:
                organism = dataset.get('organism')
                if organism and organism != 'Unknown' and organism.strip():
                    organisms_set.add(organism)
                    organism_counts[organism] = organism_counts.get(organism, 0) + 1
            
            # Sort by count (most common first)
            sorted_organisms = sorted(organism_counts.items(), key=lambda x: x[1], reverse=True)
            organism_names = [org[0] for org in sorted_organisms]
            
            logger.info(f"Found {len(organism_names)} unique organisms from NASA OSDR datasets")
            
            return {
                "organisms": organism_names,
                "source": "NASA OSDR API",
                "total": len(organism_names)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch organisms from NASA OSDR: {e}")
            return {
                "organisms": [],
                "source": "Error",
                "error": str(e),
                "total": 0
            }

    async def get_missions(self) -> Dict[str, Any]:
        """Get list of space missions from actual NASA OSDR datasets."""
        logger.info("Fetching missions from NASA OSDR datasets")
        
        try:
            # Fetch datasets to extract missions
            datasets_response = await self.get_datasets(limit=100, page=0)
            datasets = datasets_response.get('data', [])
            
            # Extract unique missions from datasets
            missions_set = set()
            mission_counts = {}
            
            for dataset in datasets:
                mission = dataset.get('mission')
                if mission and mission != 'Unknown' and mission != 'Unknown Mission' and mission.strip():
                    missions_set.add(mission)
                    mission_counts[mission] = mission_counts.get(mission, 0) + 1
            
            # Sort by count (most common first)
            sorted_missions = sorted(mission_counts.items(), key=lambda x: x[1], reverse=True)
            mission_names = [mission[0] for mission in sorted_missions]
            
            logger.info(f"Found {len(mission_names)} unique missions from NASA OSDR datasets")
            
            return {
                "missions": mission_names,
                "source": "NASA OSDR API",
                "total": len(mission_names)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch missions from NASA OSDR: {e}")
            return {
                "missions": [],
                "source": "Error",
                "error": str(e),
                "total": 0
            }

    async def get_experiments(self) -> Dict[str, Any]:
        """Get experiments from GEODE experiments API."""
        try:
            url = f"{self.geode_base}/geode-py/ws/api/experiments"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch experiments: {e}")
            return {"experiments": [], "error": str(e)}

    async def get_payloads(self) -> Dict[str, Any]:
        """Get payloads from GEODE payloads API."""
        try:
            url = f"{self.geode_base}/geode-py/ws/api/payloads"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch payloads: {e}")
            return {"payloads": [], "error": str(e)}

    async def get_hardware(self) -> Dict[str, Any]:
        """Get hardware from GEODE hardware API."""
        try:
            url = f"{self.geode_base}/geode-py/ws/api/hardware"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch hardware: {e}")
            return {"hardware": [], "error": str(e)}

    async def get_vehicles(self) -> Dict[str, Any]:
        """Get vehicles from GEODE vehicles API."""
        try:
            url = f"{self.geode_base}/geode-py/ws/api/vehicles"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch vehicles: {e}")
            return {"vehicles": [], "error": str(e)}

    async def get_biospecimens(self) -> Dict[str, Any]:
        """Get biospecimens from GEODE biospecimens API."""
        try:
            url = f"{self.geode_base}/geode-py/ws/api/biospecimens"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch biospecimens: {e}")
            return {"biospecimens": [], "error": str(e)}

    async def get_metadata(self, study_id: str) -> Dict[str, Any]:
        """Get study metadata using OSDR metadata API."""
        try:
            url = f"{self.osdr_base}/osdr/data/osd/meta/{study_id}"
            logger.info(f"Fetching metadata for study {study_id} from {url}")
            
            response = await self.client.get(url, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Metadata response keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
                
                # OSDR metadata API returns: {"hits": N, "input": "OSD-XXX", "study": {...}, "success": true}
                if isinstance(data, dict) and 'study' in data:
                    study_data = data.get('study', {})
                    if study_data:
                        logger.info(f"Found study data with {len(study_data)} fields")
                        return study_data
                    else:
                        logger.warning(f"Empty study data for {study_id}")
                        return data  # Return the whole response
                else:
                    logger.warning(f"Unexpected metadata format for {study_id}")
                    return data
            else:
                logger.error(f"Metadata API returned {response.status_code} for {study_id}")
                raise Exception(f"Metadata API returned {response.status_code}")
            
        except Exception as e:
            logger.error(f"Failed to fetch metadata for {study_id}: {e}")
            return {"error": f"Failed to fetch metadata: {str(e)}"}

    async def get_files(self, study_ids: str, page: int = 0, size: int = 25, all_files: bool = False) -> Dict[str, Any]:
        """Get file list for study using OSDR files API."""
        try:
            # NASA OSDR Files API endpoint
            url = f"{self.osdr_base}/osdr/data/osd/files/{study_ids}"
            params = {
                "page": page, 
                "size": size, 
                "all_files": str(all_files).lower()
            }
            
            logger.info(f"Fetching files for study {study_ids} from {url}")
            response = await self.client.get(url, params=params, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Files API response type: {type(data)}")
                logger.info(f"Files API response keys: {data.keys() if isinstance(data, dict) else 'list'}")
                
                # Parse the response structure
                files_list = []
                
                # OSDR returns files in different formats
                if isinstance(data, dict):
                    # Log what we got
                    logger.info(f"Response structure: {list(data.keys())}")
                    
                    # Format 1: Direct files array
                    if 'files' in data and isinstance(data['files'], list):
                        files_list = data['files']
                        logger.info(f"Found {len(files_list)} files in 'files' key")
                    # Format 2: Study files object
                    elif 'study_files' in data:
                        files_list = data['study_files']
                        logger.info(f"Found files in 'study_files' key")
                    # Format 3: Data files
                    elif 'data_files' in data:
                        files_list = data['data_files']
                        logger.info(f"Found files in 'data_files' key")
                    # Format 4: Check if the dict itself is empty (no files available)
                    elif not data or len(data) == 0:
                        logger.warning(f"Empty response from files API for {study_ids}")
                        files_list = []
                    
                    # Extract file information
                    processed_files = []
                    for file_item in files_list:
                        if isinstance(file_item, dict):
                            processed_file = {
                                "file_name": file_item.get('file_name') or file_item.get('name') or file_item.get('filename'),
                                "file_size": file_item.get('file_size') or file_item.get('size'),
                                "file_type": file_item.get('file_type') or file_item.get('type'),
                                "file_url": file_item.get('file_url') or file_item.get('url') or file_item.get('download_url'),
                                "remote_url": file_item.get('remote_url'),
                                "subdirectory": file_item.get('subdirectory') or file_item.get('path'),
                                "description": file_item.get('description')
                            }
                            processed_files.append(processed_file)
                    
                    logger.info(f"Processed {len(processed_files)} files for study {study_ids}")
                    
                    return {
                        "study_id": study_ids,
                        "files": processed_files,
                        "total": data.get('total', len(processed_files)),
                        "page": page,
                        "size": size,
                        "source": "NASA OSDR Files API",
                        "message": f"Found {len(processed_files)} files" if processed_files else "No public files available for this study"
                    }
                elif isinstance(data, list):
                    # Direct array response
                    processed_files = []
                    for file_item in data:
                        if isinstance(file_item, dict):
                            processed_file = {
                                "file_name": file_item.get('file_name') or file_item.get('name'),
                                "file_size": file_item.get('file_size') or file_item.get('size'),
                                "file_type": file_item.get('file_type') or file_item.get('type'),
                                "file_url": file_item.get('file_url') or file_item.get('url'),
                                "remote_url": file_item.get('remote_url'),
                                "subdirectory": file_item.get('subdirectory')
                            }
                            processed_files.append(processed_file)
                    
                    return {
                        "study_id": study_ids,
                        "files": processed_files,
                        "total": len(processed_files),
                        "page": page,
                        "size": size,
                        "source": "NASA OSDR Files API"
                    }
                else:
                    logger.warning(f"Unexpected file response format for {study_ids}")
                    raise Exception("Unexpected file response format")
            else:
                logger.error(f"Files API returned status {response.status_code} for {study_ids}")
                raise Exception(f"Files API returned {response.status_code}")
            
        except Exception as e:
            logger.error(f"Failed to fetch files for {study_ids}: {e}")
            
            # Return error response (NO FALLBACK)
            return {
                "study_id": study_ids,
                "files": [],
                "total": 0,
                "page": page,
                "size": size,
                "source": "Error",
                "error": f"Could not fetch files from OSDR: {str(e)}",
                "message": "This study may not have public files available yet, or the study ID may be incorrect."
            }

    async def get_study_details(self, study_id: str) -> Dict[str, Any]:
        """Get comprehensive study details combining metadata and basic info."""
        try:
            logger.info(f"Fetching comprehensive details for study {study_id}")
            
            # FIRST: Try to get from search API (has descriptions)
            try:
                search_url = f"{self.osdr_base}/osdr/data/search"
                params = {"term": study_id, "size": 1}
                
                logger.info(f"Searching for {study_id} in OSDR search API")
                response = await self.client.get(search_url, params=params, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('hits', {}).get('hits'):
                        hit = data['hits']['hits'][0]
                        source = hit.get('_source', {})
                        
                        # Check if this is the right study
                        if source.get('Study Identifier') == study_id:
                            logger.info(f"Found {study_id} in search API with full data")
                            study_data = self._transform_osdr_hit_to_dataset(hit)
                            
                            return {
                                "study_id": study_id,
                                "title": study_data.get('title', f"Study {study_id}"),
                                "description": study_data.get('description', ''),
                                "organism": study_data.get('organism'),
                                "mission": study_data.get('mission'),
                                "study_type": study_data.get('study_type'),
                                "release_date": study_data.get('release_date'),
                                "data_types": study_data.get('data_types', []),
                                "source": "NASA OSDR Search API",
                                **study_data  # Include all other fields
                            }
            except Exception as e:
                logger.warning(f"Could not fetch {study_id} from search API: {e}")
            
            # SECOND: Fall back to metadata API
            metadata = await self.get_metadata(study_id)
            
            if "error" in metadata:
                logger.warning(f"Metadata fetch failed for {study_id}")
                # Return error response (NO FALLBACK)
                return {
                    "study_id": study_id,
                    "title": f"Study {study_id}",
                    "description": "Study details unavailable from OSDR API",
                    "metadata": metadata,
                    "source": "Error",
                    "error": metadata.get("error"),
                    "message": "Could not fetch study details from NASA OSDR API"
                }
            
            # Check if metadata is actually empty (study doesn't exist or no public data)
            if not metadata or (isinstance(metadata, dict) and len(metadata) == 0):
                logger.warning(f"Study {study_id} has no metadata in OSDR")
                return {
                    "study_id": study_id,
                    "title": f"Study {study_id}",
                    "description": "This study has no public metadata available in NASA OSDR yet. It may be under embargo or in processing.",
                    "organism": None,
                    "mission": None,
                    "study_type": "Unknown",
                    "release_date": None,
                    "source": "NASA OSDR API (No Data)",
                    "message": "No public metadata available for this study"
                }
            
            # Extract key information from metadata
            study_details = {
                "study_id": study_id,
                "title": metadata.get("Study Title") or metadata.get("title") or f"Study {study_id}",
                "description": metadata.get("Study Description") or metadata.get("description") or "No description available",
                "organism": metadata.get("organism") or metadata.get("Organism"),
                "mission": metadata.get("Mission") or metadata.get("mission"),
                "study_type": metadata.get("Study Protocol Type") or metadata.get("study_type"),
                "release_date": metadata.get("Study Public Release Date") or metadata.get("release_date"),
                "managing_center": metadata.get("Managing NASA Center"),
                "funding_agency": metadata.get("Study Funding Agency"),
                "publications": metadata.get("Study Publication Title") or [],
                "data_types": [],
                "metadata": metadata,
                "timestamp": metadata.get("last_modified") or metadata.get("created_date"),
                "source": "NASA OSDR API"
            }
            
            # Extract data types
            if metadata.get("Study Assay Technology Type"):
                study_details["data_types"].append(metadata["Study Assay Technology Type"])
            if metadata.get("Study Assay Measurement Type"):
                study_details["data_types"].append(metadata["Study Assay Measurement Type"])
            
            logger.info(f"Successfully fetched complete details for {study_id}")
            return study_details
            
        except Exception as e:
            logger.error(f"Failed to get study details for {study_id}: {e}")
            return {
                "study_id": study_id,
                "title": f"Study {study_id}",
                "description": "Error fetching study details from NASA OSDR API",
                "error": str(e),
                "source": "Error",
                "message": "Failed to retrieve study information from NASA OSDR"
            }

    async def _get_sample_datasets(self) -> List[Dict[str, Any]]:
        """Get sample datasets - DEPRECATED: System now uses only real NASA OSDR data."""
        logger.warning("Sample datasets method called - this should not happen in production")
        return [
            {
                "id": "GLDS-104",
                "title": "Spaceflight Effects on Arabidopsis Gene Expression",
                "description": "Analysis of Arabidopsis thaliana grown aboard the International Space Station to understand how spaceflight affects plant gene expression and development. This study examines transcriptomic changes in plant tissues exposed to microgravity.",
                "organism": "Arabidopsis thaliana",
                "mission": "SpaceX CRS-3",
                "data_types": ["RNA-seq", "Microarray"],
                "release_date": "2023-08-15",
                "study_type": "Transcriptome",
                "publications": 3,
                "samples": 24
            },
            {
                "id": "GLDS-242",
                "title": "Microgravity-Induced Changes in Mouse Muscle",
                "description": "Investigation of muscle atrophy and protein degradation pathways in mice exposed to microgravity conditions during long-duration spaceflight missions. Focuses on skeletal muscle adaptations.",
                "organism": "Mus musculus",
                "mission": "SpaceX CRS-18",
                "data_types": ["Proteome", "Western Blot"],
                "release_date": "2023-09-22",
                "study_type": "Proteome",
                "publications": 7,
                "samples": 48
            },
            {
                "id": "GLDS-321",
                "title": "Radiation Response in Human Cell Cultures",
                "description": "Study of DNA repair mechanisms and cellular stress responses in human fibroblast cultures exposed to space radiation levels. Examines genomic stability and repair pathway activation.",
                "organism": "Homo sapiens",
                "mission": "ISS Expedition 65",
                "data_types": ["RNA-seq", "ChIP-seq", "ATAC-seq"],
                "release_date": "2023-11-10",
                "study_type": "Multi-omics",
                "publications": 5,
                "samples": 36
            },
            {
                "id": "GLDS-158",
                "title": "Fruit Fly Circadian Rhythms in Space",
                "description": "Analysis of circadian clock disruption in Drosophila melanogaster during spaceflight. Investigates changes in sleep-wake cycles and clock gene expression patterns in microgravity.",
                "organism": "Drosophila melanogaster",
                "mission": "SpaceX CRS-12",
                "data_types": ["RNA-seq", "Behavioral Analysis"],
                "release_date": "2023-07-30",
                "study_type": "Behavioral Genomics",
                "publications": 4,
                "samples": 72
            },
            {
                "id": "GLDS-275",
                "title": "Bone Density Loss in Rat Models",
                "description": "Comprehensive analysis of bone mineral density changes and osteoblast activity in rats during extended exposure to microgravity conditions. Studies calcium metabolism and bone formation.",
                "organism": "Rattus norvegicus",
                "mission": "SpaceX CRS-21",
                "data_types": ["MicroCT", "Histology", "qPCR"],
                "release_date": "2023-10-05",
                "study_type": "Physiology",
                "publications": 6,
                "samples": 60
            },
            {
                "id": "GLDS-199",
                "title": "Microbial Community Changes in Space",
                "description": "Metagenomic analysis of microbial communities aboard the International Space Station. Examines how microgravity and radiation affect bacterial growth patterns and antibiotic resistance.",
                "organism": "Escherichia coli",
                "mission": "ISS Expedition 63",
                "data_types": ["16S rRNA", "Metagenomics"],
                "release_date": "2023-06-18",
                "study_type": "Microbiome",
                "publications": 8,
                "samples": 144
            },
            {
                "id": "GLDS-87",
                "title": "Yeast Cell Cycle in Microgravity",
                "description": "Investigation of cell division and cell cycle regulation in Saccharomyces cerevisiae under microgravity conditions. Studies cell wall formation and budding patterns.",
                "organism": "Saccharomyces cerevisiae",
                "mission": "SpaceX CRS-8",
                "data_types": ["RNA-seq", "Flow Cytometry"],
                "release_date": "2023-05-12",
                "study_type": "Cell Biology",
                "publications": 2,
                "samples": 18
            },
            {
                "id": "GLDS-312",
                "title": "Nematode Aging in Space Environment",
                "description": "Long-term study of aging processes and lifespan in C. elegans exposed to spaceflight conditions. Examines oxidative stress responses and longevity gene expression.",
                "organism": "Caenorhabditis elegans",
                "mission": "SpaceX CRS-24",
                "data_types": ["RNA-seq", "Lifespan Analysis"],
                "release_date": "2024-01-08",
                "study_type": "Aging Research",
                "publications": 3,
                "samples": 96
            }
        ]

    async def close(self):
        """Close the HTTP client connection."""
        try:
            await self.client.aclose()
            logger.info("NASA client connection closed")
        except Exception as e:
            logger.error(f"Error closing NASA client: {e}")
