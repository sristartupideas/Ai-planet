"""
Web Search Tool using Serper API for comprehensive market research
"""
import requests
from typing import Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class WebSearchTool:
    """Tool for performing web searches using Serper API"""
    
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
    
    def _run(self, query: str) -> str:
        """
        Perform web search using Serper API
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results
        """
        try:
            if not self.api_key:
                return "Serper API key not configured. Please set SERPER_API_KEY in environment variables."
            
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': 10
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_results(data, query)
            else:
                logger.error(f"Serper API error: {response.status_code} - {response.text}")
                return f"Search failed with status {response.status_code}"
                
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return f"Search failed: {str(e)}"
    
    def _format_results(self, data: Dict[str, Any], query: str) -> str:
        """Format search results for display"""
        try:
            results = []
            results.append(f"=== WEB SEARCH RESULTS FOR: '{query}' ===\n")
            
            organic_results = data.get('organic', [])
            if not organic_results:
                return f"No results found for query: '{query}'"
            
            results.append(f"📊 Found {len(organic_results)} results:\n")
            
            for i, result in enumerate(organic_results[:10], 1):
                title = result.get('title', 'No title')
                link = result.get('link', '')
                snippet = result.get('snippet', 'No description')
                
                results.append(f"{i}. **{title}**")
                results.append(f"   🔗 {link}")
                results.append(f"   📝 {snippet}")
                results.append("")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Error formatting results: {str(e)}")
            return f"Found results but failed to format: {str(e)}"