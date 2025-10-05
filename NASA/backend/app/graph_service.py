"""Graph Service for NASA Space Biology Knowledge Engine.

Provides knowledge graph operations with Neo4j primary and SQLite fallback.
Manages relationships between studies, organisms, missions, and research data.
"""

from typing import Any, Dict, List, Optional, Tuple
from .config import settings, logger
import asyncio
import aiosqlite
import json
import os
import hashlib
from datetime import datetime

# Optional Neo4j import
try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available, using SQLite fallback")

class SQLiteGraph:
    """SQLite-based graph database for storing nodes and relationships."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialized = False
    
    async def init(self):
        """Initialize SQLite graph database."""
        if self._initialized:
            return
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Create nodes table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS nodes (
                        id TEXT PRIMARY KEY,
                        label TEXT NOT NULL,
                        type TEXT NOT NULL,
                        properties TEXT,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL
                    )
                """)
                
                # Create edges table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS edges (
                        id TEXT PRIMARY KEY,
                        source_id TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        label TEXT NOT NULL,
                        properties TEXT,
                        created_at REAL NOT NULL,
                        FOREIGN KEY (source_id) REFERENCES nodes (id),
                        FOREIGN KEY (target_id) REFERENCES nodes (id)
                    )
                """)
                
                # Create indexes
                await db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_edges_label ON edges(label)")
                
                await db.commit()
            
            self._initialized = True
            logger.info(f"SQLite graph initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQLite graph: {e}")
            raise
    
    async def add_node(self, node_id: str, label: str, node_type: str, properties: Dict[str, Any] = None) -> bool:
        """Add a node to the graph."""
        if not self._initialized:
            await self.init()
        
        try:
            current_time = datetime.now().timestamp()
            props_json = json.dumps(properties or {})
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO nodes (id, label, type, properties, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (node_id, label, node_type, props_json, current_time, current_time)
                )
                await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")
            return False
    
    async def add_edge(self, source_id: str, target_id: str, label: str, properties: Dict[str, Any] = None) -> bool:
        """Add an edge between two nodes."""
        if not self._initialized:
            await self.init()
        
        try:
            # Generate edge ID
            edge_id = hashlib.md5(f"{source_id}_{target_id}_{label}".encode()).hexdigest()
            current_time = datetime.now().timestamp()
            props_json = json.dumps(properties or {})
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO edges (id, source_id, target_id, label, properties, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (edge_id, source_id, target_id, label, props_json, current_time)
                )
                await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add edge {source_id}->{target_id}: {e}")
            return False
    
    async def get_nodes(self, node_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get nodes from the graph with optional type filtering."""
        if not self._initialized:
            await self.init()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if node_type:
                    query = "SELECT id, label, type, properties FROM nodes WHERE type = ? LIMIT ?"
                    params = (node_type, limit)
                else:
                    query = "SELECT id, label, type, properties FROM nodes LIMIT ?"
                    params = (limit,)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                nodes = []
                for row in rows:
                    node = {
                        "id": row[0],
                        "label": row[1],
                        "type": row[2],
                        "properties": json.loads(row[3]) if row[3] else {}
                    }
                    nodes.append(node)
                    
                return nodes
                
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return []
    
    async def get_edges(self, source_id: str = None, target_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get edges from the graph with optional filtering."""
        if not self._initialized:
            await self.init()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = "SELECT id, source_id, target_id, label, properties FROM edges"
                params = []
                
                if source_id and target_id:
                    query += " WHERE source_id = ? AND target_id = ?"
                    params = [source_id, target_id]
                elif source_id:
                    query += " WHERE source_id = ?"
                    params = [source_id]
                elif target_id:
                    query += " WHERE target_id = ?"
                    params = [target_id]
                
                query += " LIMIT ?"
                params.append(limit)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                edges = []
                for row in rows:
                    edge = {
                        "id": row[0],
                        "source": row[1],
                        "target": row[2],
                        "label": row[3],
                        "properties": json.loads(row[4]) if row[4] else {}
                    }
                    edges.append(edge)
                    
                return edges
                
        except Exception as e:
            logger.error(f"Failed to get edges: {e}")
            return []
    
    async def get_graph(self, limit: int = 100) -> Dict[str, Any]:
        """Get complete graph data with nodes and edges."""
        nodes = await self.get_nodes(limit=limit)
        edges = await self.get_edges(limit=limit)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
    
    async def search_nodes(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search nodes by label or properties."""
        if not self._initialized:
            await self.init()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                search_query = """
                    SELECT id, label, type, properties 
                    FROM nodes 
                    WHERE label LIKE ? OR properties LIKE ?
                    LIMIT ?
                """
                search_term = f"%{query}%"
                
                async with db.execute(search_query, (search_term, search_term, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
                nodes = []
                for row in rows:
                    node = {
                        "id": row[0],
                        "label": row[1],
                        "type": row[2],
                        "properties": json.loads(row[3]) if row[3] else {}
                    }
                    nodes.append(node)
                    
                return nodes
                
        except Exception as e:
            logger.error(f"Failed to search nodes: {e}")
            return []

class GraphService:
    """Knowledge graph service with Neo4j primary and SQLite fallback."""
    
    def __init__(self):
        self.neo4j_driver = None
        
        # Try to initialize Neo4j if available
        if (NEO4J_AVAILABLE and settings.neo4j_uri and 
            settings.neo4j_user and settings.neo4j_password):
            try:
                self.neo4j_driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password)
                )
                logger.info("Neo4j driver initialized")
            except Exception as e:
                logger.warning(f"Neo4j initialization failed: {e}")
        
        # SQLite fallback
        sqlite_path = os.path.join(settings.data_dir, "graph.db")
        self.sqlite_graph = SQLiteGraph(sqlite_path)
        
        # Initialize with NASA data structure
        self._setup_graph_structure()
        
        logger.info(f"Graph service configured:")
        logger.info(f"  - Neo4j: {'✓' if self.neo4j_driver else '✗'}")
        logger.info(f"  - SQLite: ✓ (at {sqlite_path})")
    
    def _setup_graph_structure(self):
        """Set up the basic graph structure for NASA space biology data."""
        # This will be called during initialization
        pass
    
    async def init(self):
        """Initialize graph service and test connections."""
        # Test Neo4j connection if available
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    result = await session.run("RETURN 1 as test")
                    await result.single()
                logger.info("Neo4j connection tested successfully")
            except Exception as e:
                logger.error(f"Neo4j connection test failed: {e}")
                self.neo4j_driver = None
        
        # Initialize SQLite fallback
        await self.sqlite_graph.init()
        
        # Check existing graph data (NO SAMPLE DATA CREATION)
        try:
            existing_nodes = await self.sqlite_graph.get_nodes(limit=1)
            if existing_nodes:
                logger.info(f"Found existing graph data with {len(await self.sqlite_graph.get_nodes())} nodes")
            else:
                logger.info("Graph is empty - will be populated from NASA OSDR datasets")
        except Exception as e:
            logger.error(f"Failed to check graph data: {e}")
    
    async def add_study_node(self, study_id: str, study_data: Dict[str, Any]) -> bool:
        """Add a study node to the knowledge graph."""
        node_id = f"study_{study_id}"
        label = study_data.get('title', study_id)
        properties = {
            "study_id": study_id,
            "title": study_data.get('title'),
            "description": study_data.get('description'),
            "organism": study_data.get('organism'),
            "mission": study_data.get('mission')
        }
        
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    await session.run(
                        "MERGE (s:Study {id: $id}) SET s.label = $label, s.properties = $props",
                        id=node_id, label=label, props=json.dumps(properties)
                    )
                return True
            except Exception as e:
                logger.error(f"Neo4j add study failed: {e}")
        
        # Fallback to SQLite
        return await self.sqlite_graph.add_node(node_id, label, "study", properties)
    
    async def add_organism_node(self, organism_name: str) -> bool:
        """Add an organism node to the knowledge graph."""
        node_id = f"organism_{organism_name.replace(' ', '_').lower()}"
        
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    await session.run(
                        "MERGE (o:Organism {id: $id}) SET o.label = $label",
                        id=node_id, label=organism_name
                    )
                return True
            except Exception as e:
                logger.error(f"Neo4j add organism failed: {e}")
        
        # Fallback to SQLite
        return await self.sqlite_graph.add_node(
            node_id, organism_name, "organism", {"name": organism_name}
        )
    
    async def add_mission_node(self, mission_name: str) -> bool:
        """Add a mission node to the knowledge graph."""
        node_id = f"mission_{mission_name.replace(' ', '_').lower()}"
        
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    await session.run(
                        "MERGE (m:Mission {id: $id}) SET m.label = $label",
                        id=node_id, label=mission_name
                    )
                return True
            except Exception as e:
                logger.error(f"Neo4j add mission failed: {e}")
        
        # Fallback to SQLite
        return await self.sqlite_graph.add_node(
            node_id, mission_name, "mission", {"name": mission_name}
        )
    
    async def link_study_organism(self, study_id: str, organism_name: str) -> bool:
        """Link a study to an organism."""
        study_node_id = f"study_{study_id}"
        organism_node_id = f"organism_{organism_name.replace(' ', '_').lower()}"
        
        # Ensure organism node exists
        await self.add_organism_node(organism_name)
        
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    await session.run(
                        "MATCH (s:Study {id: $study_id}), (o:Organism {id: $organism_id}) "
                        "MERGE (s)-[:STUDIES]->(o)",
                        study_id=study_node_id, organism_id=organism_node_id
                    )
                return True
            except Exception as e:
                logger.error(f"Neo4j link study-organism failed: {e}")
        
        # Fallback to SQLite
        return await self.sqlite_graph.add_edge(
            study_node_id, organism_node_id, "studies"
        )
    
    async def link_study_mission(self, study_id: str, mission_name: str) -> bool:
        """Link a study to a mission."""
        study_node_id = f"study_{study_id}"
        mission_node_id = f"mission_{mission_name.replace(' ', '_').lower()}"
        
        # Ensure mission node exists
        await self.add_mission_node(mission_name)
        
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    await session.run(
                        "MATCH (s:Study {id: $study_id}), (m:Mission {id: $mission_id}) "
                        "MERGE (s)-[:CONDUCTED_ON]->(m)",
                        study_id=study_node_id, mission_id=mission_node_id
                    )
                return True
            except Exception as e:
                logger.error(f"Neo4j link study-mission failed: {e}")
        
        # Fallback to SQLite
        return await self.sqlite_graph.add_edge(
            study_node_id, mission_node_id, "conducted_on"
        )
    
    async def create_sample_graph(self) -> bool:
        """DEPRECATED: Sample graph data removed - graph now built from real NASA OSDR data only."""
        logger.warning("create_sample_graph() called but is deprecated - use real NASA data")
        return False
        
        # REMOVED: Sample data creation - graph is now built dynamically from NASA OSDR
        try:
            logger.info("Creating sample graph data (DEPRECATED)")
            
            # Sample studies from our datasets
            studies = [
                {"id": "GLDS-104", "title": "Spaceflight Effects on Arabidopsis Gene Expression", 
                 "organism": "Arabidopsis thaliana", "mission": "SpaceX CRS-3"},
                {"id": "GLDS-242", "title": "Microgravity-Induced Changes in Mouse Muscle", 
                 "organism": "Mus musculus", "mission": "SpaceX CRS-18"},
                {"id": "GLDS-321", "title": "Radiation Response in Human Cell Cultures", 
                 "organism": "Homo sapiens", "mission": "ISS Expedition 65"},
                {"id": "GLDS-158", "title": "Fruit Fly Circadian Rhythms in Space", 
                 "organism": "Drosophila melanogaster", "mission": "SpaceX CRS-12"},
                {"id": "GLDS-275", "title": "Bone Density Loss in Rat Models", 
                 "organism": "Rattus norvegicus", "mission": "SpaceX CRS-21"},
                {"id": "GLDS-199", "title": "Microbial Community Changes in Space", 
                 "organism": "Escherichia coli", "mission": "ISS Expedition 63"}
            ]
            
            # Add all study nodes and create relationships
            for study in studies:
                await self.add_study_node(study["id"], study)
                if study["organism"]:
                    await self.link_study_organism(study["id"], study["organism"])
                if study["mission"]:
                    await self.link_study_mission(study["id"], study["mission"])
            
            # Add some research area nodes
            research_areas = [
                "Microgravity Effects", "Space Radiation", "Circadian Rhythms", 
                "Bone Density", "Muscle Atrophy", "Gene Expression"
            ]
            
            for area in research_areas:
                area_id = f"research_{area.replace(' ', '_').lower()}"
                await self.sqlite_graph.add_node(area_id, area, "research_area", {"name": area})
            
            # Link studies to research areas
            study_area_links = [
                ("GLDS-104", "Gene Expression"),
                ("GLDS-104", "Microgravity Effects"),
                ("GLDS-242", "Muscle Atrophy"),
                ("GLDS-242", "Microgravity Effects"),
                ("GLDS-321", "Space Radiation"),
                ("GLDS-158", "Circadian Rhythms"),
                ("GLDS-275", "Bone Density"),
                ("GLDS-275", "Microgravity Effects")
            ]
            
            for study_id, area in study_area_links:
                study_node_id = f"study_{study_id}"
                area_node_id = f"research_{area.replace(' ', '_').lower()}"
                await self.sqlite_graph.add_edge(study_node_id, area_node_id, "investigates")
            
            logger.info("Sample graph data created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample graph: {e}")
            return False
    
    async def get_graph(self, limit: int = 100) -> Dict[str, Any]:
        """Get graph data for visualization."""
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    # Get nodes and relationships
                    query = """
                        MATCH (n)-[r]-(m) 
                        RETURN n, r, m 
                        LIMIT $limit
                    """
                    result = await session.run(query, limit=limit)
                    
                    nodes = {}
                    edges = []
                    
                    async for record in result:
                        n = record["n"]
                        m = record["m"]
                        r = record["r"]
                        
                        # Add nodes
                        for node in (n, m):
                            node_id = str(node.id)
                            if node_id not in nodes:
                                nodes[node_id] = {
                                    "id": node_id,
                                    "label": node.get("label", node.get("name", node_id)),
                                    "type": list(node.labels)[0].lower() if node.labels else "unknown"
                                }
                        
                        # Add edge
                        edges.append({
                            "id": str(r.id),
                            "source": str(n.id),
                            "target": str(m.id),
                            "label": r.type.lower().replace('_', ' ')
                        })
                    
                    return {
                        "nodes": list(nodes.values()),
                        "edges": edges,
                        "provider": "neo4j"
                    }
                    
            except Exception as e:
                logger.error(f"Neo4j get graph failed: {e}")
        
        # Fallback to SQLite
        graph_data = await self.sqlite_graph.get_graph(limit)
        graph_data["provider"] = "sqlite"
        return graph_data
    
    async def search_graph(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """Search the knowledge graph."""
        # Try Neo4j first
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    search_query = """
                        MATCH (n) 
                        WHERE n.label CONTAINS $query OR n.name CONTAINS $query
                        RETURN n
                        LIMIT $limit
                    """
                    result = await session.run(search_query, query=query, limit=limit)
                    
                    nodes = []
                    async for record in result:
                        node = record["n"]
                        nodes.append({
                            "id": str(node.id),
                            "label": node.get("label", node.get("name", str(node.id))),
                            "type": list(node.labels)[0].lower() if node.labels else "unknown"
                        })
                    
                    return {
                        "nodes": nodes,
                        "provider": "neo4j"
                    }
                    
            except Exception as e:
                logger.error(f"Neo4j search failed: {e}")
        
        # Fallback to SQLite
        nodes = await self.sqlite_graph.search_nodes(query, limit)
        return {
            "nodes": nodes,
            "provider": "sqlite"
        }
    
    async def build_graph_from_data(self, studies: List[Dict[str, Any]]) -> bool:
        """Build knowledge graph from NASA study data."""
        try:
            for study in studies:
                study_id = study.get('id') or study.get('study_id')
                if not study_id:
                    continue
                
                # Add study node
                await self.add_study_node(study_id, study)
                
                # Link to organism if available
                organism = study.get('organism')
                if organism:
                    await self.link_study_organism(study_id, organism)
                
                # Link to mission if available
                mission = study.get('mission')
                if mission:
                    await self.link_study_mission(study_id, mission)
            
            logger.info(f"Built graph from {len(studies)} studies")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build graph from data: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        stats = {
            "neo4j_available": self.neo4j_driver is not None,
            "sqlite_available": self.sqlite_graph._initialized
        }
        
        # Get node/edge counts
        if self.neo4j_driver:
            try:
                async with self.neo4j_driver.session() as session:
                    # Count nodes
                    result = await session.run("MATCH (n) RETURN count(n) as node_count")
                    record = await result.single()
                    stats["neo4j_node_count"] = record["node_count"]
                    
                    # Count edges
                    result = await session.run("MATCH ()-[r]->() RETURN count(r) as edge_count")
                    record = await result.single()
                    stats["neo4j_edge_count"] = record["edge_count"]
            except Exception as e:
                logger.error(f"Failed to get Neo4j stats: {e}")
        
        # SQLite stats
        try:
            graph_data = await self.sqlite_graph.get_graph(limit=1000)
            stats["sqlite_node_count"] = len(graph_data["nodes"])
            stats["sqlite_edge_count"] = len(graph_data["edges"])
        except Exception as e:
            logger.error(f"Failed to get SQLite stats: {e}")
        
        return stats
    
    async def close(self):
        """Close graph service connections."""
        if self.neo4j_driver:
            try:
                await self.neo4j_driver.close()
                logger.info("Neo4j driver closed")
            except Exception as e:
                logger.error(f"Error closing Neo4j driver: {e}")
