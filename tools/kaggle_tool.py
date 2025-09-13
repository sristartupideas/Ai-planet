"""
Kaggle Dataset Search Tool for finding relevant datasets
"""
import requests
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class KaggleTool:
    """Tool for searching Kaggle datasets"""
    
    def __init__(self):
        self.username = settings.KAGGLE_USERNAME
        self.api_key = settings.KAGGLE_KEY
        self.base_url = "https://www.kaggle.com/api/v1"
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """
        Search for datasets on Kaggle
        
        Args:
            query: Search query for datasets
            max_results: Maximum number of results to return
            
        Returns:
            Formatted dataset information
        """
        try:
            if not self.api_key or not self.username:
                return "Kaggle API credentials not configured. Please set KAGGLE_USERNAME and KAGGLE_KEY in environment variables."
            
            headers = {
                'Authorization': f'Basic {self._get_auth_token()}',
                'Content-Type': 'application/json'
            }
            
            # Search datasets
            search_url = f"{self.base_url}/datasets/list"
            params = {
                'search': query,
                'pageSize': max_results,
                'sortBy': 'relevance'
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_dataset_results(data, query)
            else:
                logger.error(f"Kaggle API error: {response.status_code} - {response.text}")
                return f"Kaggle search failed with status {response.status_code}"
                
        except Exception as e:
            logger.error(f"Kaggle search error: {str(e)}")
            return f"Kaggle search failed: {str(e)}"
    
    def _get_auth_token(self) -> str:
        """Get base64 encoded auth token for Kaggle API"""
        import base64
        credentials = f"{self.username}:{self.api_key}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _format_dataset_results(self, data: List[Dict[str, Any]], query: str) -> str:
        """Format Kaggle dataset results"""
        try:
            results = []
            results.append(f"=== KAGGLE DATASETS FOR: '{query}' ===\n")
            
            if not data:
                return f"No datasets found for query: '{query}'"
            
            results.append(f"📊 Found {len(data)} datasets:\n")
            
            for i, dataset in enumerate(data, 1):
                title = dataset.get('title', 'No title')
                owner = dataset.get('owner', 'Unknown')
                url = f"https://www.kaggle.com/datasets/{owner}/{dataset.get('name', '')}"
                size = dataset.get('size', 'Unknown size')
                downloads = dataset.get('downloadCount', 0)
                tags = dataset.get('tags', [])
                
                results.append(f"{i}. **{title}**")
                results.append(f"   👤 Owner: {owner}")
                results.append(f"   📊 Size: {size}")
                results.append(f"   ⬇️ Downloads: {downloads:,}")
                if tags:
                    results.append(f"   🏷️ Tags: {', '.join(tags[:5])}")
                results.append(f"   🔗 URL: {url}")
                results.append("")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Error formatting Kaggle results: {str(e)}")
            return f"Found datasets but failed to format: {str(e)}"