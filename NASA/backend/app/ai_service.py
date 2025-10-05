"""AI Service for NASA Space Biology Knowledge Engine.

Provides AI-powered summarization, intent parsing, and analysis using
Google Gemini API with graceful fallbacks for offline operation.
"""

import httpx
from typing import Optional, Dict, Any, List
from .config import settings, logger
import json
import re
import asyncio

class AIService:
    """AI service with Gemini API integration and intelligent fallbacks."""
    
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.openai_api_key = settings.openai_api_key
        
        # Gemini configuration
        self.gemini_model = "gemini-1.5-pro"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Create HTTP client
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"AI Service initialized:")
        logger.info(f"  - Gemini API: {'✓' if self.gemini_api_key else '✗'}")
        logger.info(f"  - OpenAI API: {'✓' if self.openai_api_key else '✗'}")

    async def summarize(self, text: str, max_tokens: int = 512) -> Dict[str, Any]:
        """Generate AI summary of scientific text with multiple fallbacks."""
        
        # Try Gemini first
        if self.gemini_api_key:
            try:
                return await self._summarize_with_gemini(text, max_tokens)
            except Exception as e:
                logger.warning(f"Gemini summarization failed: {e}")
        
        # Try OpenAI as fallback
        if self.openai_api_key:
            try:
                return await self._summarize_with_openai(text, max_tokens)
            except Exception as e:
                logger.warning(f"OpenAI summarization failed: {e}")
        
        # Enhanced local processing (no fallback message)
        return self._summarize_locally(text)
    
    async def _summarize_with_gemini(self, text: str, max_tokens: int) -> Dict[str, Any]:
        """Summarize using Gemini API."""
        url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Analyze and summarize the following NASA space biology research data/text. 
                    Provide key insights about the research, methodology, and findings. 
                    Focus on biological significance and space-related implications:
                    
                    {text[:2000]}  
                    
                    Format your response as structured bullet points highlighting:
                    • Research focus and objectives
                    • Key biological findings
                    • Space environment implications
                    """
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.gemini_api_key
        }
        response = await self._client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract content from Gemini response
        if "candidates" in data and data["candidates"]:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                summary = candidate["content"]["parts"][0].get("text", "")
                return {
                    "summary": summary.strip(),
                    "provider": "gemini",
                    "model": self.gemini_model
                }
        
        raise Exception("Invalid Gemini API response structure")
    
    async def _summarize_with_openai(self, text: str, max_tokens: int) -> Dict[str, Any]:
        """Summarize using OpenAI API as fallback."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"Summarize this NASA space biology research in 3-4 bullet points: {text[:2000]}"
            }],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = await self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        summary = data["choices"][0]["message"]["content"]
        return {
            "summary": summary.strip(),
            "provider": "openai",
            "model": "gpt-3.5-turbo"
        }
    
    def _summarize_locally(self, text: str) -> Dict[str, Any]:
        """Local fallback summarization using simple text processing."""
        # Extract key sentences using simple heuristics
        sentences = re.split(r'[.!?]', text)
        key_terms = ['microgravity', 'space', 'protein', 'cell', 'gene', 'RNA', 'DNA', 
                    'experiment', 'study', 'analysis', 'biological', 'organism']
        
        scored_sentences = []
        for sentence in sentences[:10]:  # Limit processing
            sentence = sentence.strip()
            if len(sentence) > 20:
                score = sum(1 for term in key_terms if term.lower() in sentence.lower())
                scored_sentences.append((score, sentence))
        
        # Select top sentences
        scored_sentences.sort(reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:3]]
        
        summary = "\n• ".join(top_sentences)
        if summary:
            summary = "• " + summary
        else:
            summary = text[:400] + "..." if len(text) > 400 else text
        
        return {
            "summary": summary,
            "provider": "local_processing",
            "model": "text_analysis"
        }

    async def parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse natural language query to extract search intent and filters."""
        
        # Try Gemini first
        if self.gemini_api_key:
            try:
                return await self._parse_intent_with_gemini(query)
            except Exception as e:
                logger.warning(f"Gemini intent parsing failed: {e}")
        
        # Try OpenAI as fallback
        if self.openai_api_key:
            try:
                return await self._parse_intent_with_openai(query)
            except Exception as e:
                logger.warning(f"OpenAI intent parsing failed: {e}")
        
        # Local fallback
        return self._parse_intent_locally(query)
    
    async def _parse_intent_with_gemini(self, query: str) -> Dict[str, Any]:
        """Parse intent using Gemini API."""
        url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Extract search parameters from this NASA space biology query. Return ONLY a JSON object.
                    
                    Query: "{query}"
                    
                    Extract these fields if mentioned:
                    - query: refined search terms
                    - organisms: list of organisms mentioned
                    - missions: list of space missions mentioned
                    - tags: list of research areas (microgravity, radiation, protein, cell, gene, etc.)
                    
                    Return valid JSON only:"""
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 256,
                "temperature": 0.3
            }
        }
        
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "candidates" in data and data["candidates"]:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                text = candidate["content"]["parts"][0].get("text", "")
                # Extract JSON from response
                json_match = re.search(r'\{[^}]*\}', text, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        parsed["original_query"] = query
                        parsed["provider"] = "gemini"
                        return parsed
                    except json.JSONDecodeError:
                        pass
        
        raise Exception("Failed to parse intent from Gemini response")
    
    async def _parse_intent_with_openai(self, query: str) -> Dict[str, Any]:
        """Parse intent using OpenAI API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_api_key}"}
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"""Extract search parameters from this query and return only JSON:
                Query: "{query}"
                
                Return JSON with these fields if mentioned: query, organisms, missions, tags
                """
            }],
            "max_tokens": 256,
            "temperature": 0.3
        }
        
        response = await self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        text = data["choices"][0]["message"]["content"]
        json_match = re.search(r'\{[^}]*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                parsed["original_query"] = query
                parsed["provider"] = "openai"
                return parsed
            except json.JSONDecodeError:
                pass
        
        raise Exception("Failed to parse intent from OpenAI response")
    
    def _parse_intent_locally(self, query: str) -> Dict[str, Any]:
        """Local fallback for intent parsing using keyword matching."""
        query_lower = query.lower()
        intent = {
            "query": query,
            "original_query": query,
            "provider": "local_fallback"
        }
        
        # Extract organisms
        organisms = []
        organism_keywords = {
            "human": "Homo sapiens", "mouse": "Mus musculus", "mice": "Mus musculus",
            "arabidopsis": "Arabidopsis thaliana", "fruit fly": "Drosophila melanogaster",
            "yeast": "Saccharomyces cerevisiae", "c. elegans": "Caenorhabditis elegans"
        }
        for keyword, organism in organism_keywords.items():
            if keyword in query_lower:
                organisms.append(organism)
        if organisms:
            intent["organisms"] = organisms
        
        # Extract missions
        missions = []
        mission_keywords = ["iss", "expedition", "sts", "shuttle", "spacex", "dragon"]
        for keyword in mission_keywords:
            if keyword in query_lower:
                missions.append(keyword.upper())
        if missions:
            intent["missions"] = missions
        
        # Extract research tags
        tags = []
        tag_keywords = [
            "microgravity", "radiation", "protein", "cell", "gene", "rna", "dna",
            "muscle", "bone", "immune", "cardiovascular", "neurological"
        ]
        for tag in tag_keywords:
            if tag in query_lower:
                tags.append(tag)
        if tags:
            intent["tags"] = tags
        
        return intent
    
    async def generate_insights(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from space biology data."""
        if not data:
            return {"insights": [], "provider": "none"}
        
        # Create summary of data for AI analysis
        data_summary = "\n".join([
            f"Study: {item.get('title', 'Unknown')} - {item.get('description', '')[:100]}"
            for item in data[:5]  # Limit to prevent token overflow
        ])
        
        if self.gemini_api_key:
            try:
                return await self._generate_insights_with_gemini(data_summary)
            except Exception as e:
                logger.warning(f"Gemini insights generation failed: {e}")
        
        return self._generate_insights_locally(data)
    
    async def _generate_insights_with_gemini(self, data_summary: str) -> Dict[str, Any]:
        """Generate insights using Gemini API."""
        url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""Analyze these NASA space biology studies and generate key insights:
                    
                    {data_summary}
                    
                    Provide 3-5 analytical insights about:
                    - Common research themes
                    - Biological implications of space environment
                    - Research trends and patterns
                    
                    Format as bullet points."""
                }]
            }],
            "generationConfig": {
                "maxOutputTokens": 512,
                "temperature": 0.8
            }
        }
        
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "candidates" in data and data["candidates"]:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                insights_text = candidate["content"]["parts"][0].get("text", "")
                insights = [line.strip() for line in insights_text.split('\n') if line.strip()]
                return {
                    "insights": insights,
                    "provider": "gemini",
                    "model": self.gemini_model
                }
        
        raise Exception("Invalid Gemini insights response")
    
    def _generate_insights_locally(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic insights using local analysis."""
        insights = []
        
        # Count organisms
        organisms = {}
        missions = {}
        
        for item in data:
            organism = item.get('organism')
            if organism:
                organisms[organism] = organisms.get(organism, 0) + 1
            
            mission = item.get('mission')
            if mission:
                missions[mission] = missions.get(mission, 0) + 1
        
        if organisms:
            top_organism = max(organisms, key=organisms.get)
            insights.append(f"Most studied organism: {top_organism} ({organisms[top_organism]} studies)")
        
        if missions:
            top_mission = max(missions, key=missions.get)
            insights.append(f"Most data from mission: {top_mission} ({missions[top_mission]} studies)")
        
        insights.append(f"Total datasets analyzed: {len(data)}")
        
        return {
            "insights": insights,
            "provider": "local_analysis",
            "model": "statistical_analysis"
        }

    async def close(self):
        """Close the HTTP client connection."""
        try:
            await self._client.aclose()
            logger.info("AI service client closed")
        except Exception as e:
            logger.error(f"Error closing AI service client: {e}")
