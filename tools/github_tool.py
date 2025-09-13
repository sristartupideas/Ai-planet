"""
GitHub Repository Search Tool for finding implementation examples and code resources
"""
import requests
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class GitHubTool:
    """Tool for searching GitHub repositories for implementation examples"""
    
    def __init__(self):
        self.api_token = settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Multi-Agent-AI-System"
        }
        
        if self.api_token:
            self.headers["Authorization"] = f"token {self.api_token}"
    
    def _run(self, query: str, max_results: int = 3, language: str = "", sort: str = "stars") -> str:
        """
        Search for repositories on GitHub with improved business-relevant queries
        
        Args:
            query: Search query for repositories
            max_results: Maximum number of results to return
            language: Programming language filter
            sort: Sort criteria for results
            
        Returns:
            Formatted repository information
        """
        try:
            # Create more specific business-relevant search queries
            business_queries = [
                f"{query} business analytics",
                f"{query} enterprise software",
                f"{query} CRM system",
                f"{query} business intelligence",
                f"{query} data analytics",
                f"{query} machine learning business",
                f"{query} AI enterprise",
                f"{query} business automation",
                f"{query} predictive analytics",
                f"{query} business dashboard"
            ]
            
            all_repositories = []
            searched_queries = []
            
            for business_query in business_queries:
                try:
                    # Build search query
                    search_query = business_query
                    if language:
                        search_query += f" language:{language}"
                    
                    # Prepare request parameters
                    params = {
                        "q": search_query,
                        "sort": sort,
                        "order": "desc",
                        "per_page": min(3, 30)  # Take top 3 from each query
                    }
                    
                    # Make API request
                    response = requests.get(
                        f"{self.base_url}/search/repositories",
                        headers=self.headers,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 401:
                        logger.warning("GitHub API authentication failed, using unauthenticated requests")
                        # Remove auth header and retry
                        headers_no_auth = {k: v for k, v in self.headers.items() if k != "Authorization"}
                        response = requests.get(
                            f"{self.base_url}/search/repositories",
                            headers=headers_no_auth,
                            params=params,
                            timeout=30
                        )
                    
                    if response.status_code == 200:
                        data = response.json()
                        repositories = data.get("items", [])
                        if repositories:
                            all_repositories.extend(repositories)
                            searched_queries.append(business_query)
                    else:
                        logger.warning(f"GitHub API error for query '{business_query}': {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Error searching for '{business_query}': {str(e)}")
                    continue
            
            # Remove duplicates based on repository ID
            unique_repositories = []
            seen_ids = set()
            for repo in all_repositories:
                repo_id = repo.get("id")
                if repo_id and repo_id not in seen_ids:
                    unique_repositories.append(repo)
                    seen_ids.add(repo_id)
            
            if not unique_repositories:
                return f"No relevant business repositories found for query: '{query}'. Searched: {', '.join(business_queries)}"
            
            # Create mock data structure for formatting
            mock_data = {
                "items": unique_repositories[:max_results],
                "total_count": len(unique_repositories)
            }
            
            return self._format_repository_results(mock_data, query, searched_queries)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during GitHub search: {str(e)}")
            return f"GitHub search request failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during GitHub search: {str(e)}")
            return f"GitHub search failed with error: {str(e)}"
    
    def _format_repository_results(self, data: Dict[str, Any], query: str, searched_queries: List[str] = None) -> str:
        """Format GitHub repository results"""
        try:
            results = []
            results.append(f"=== GITHUB BUSINESS REPOSITORIES FOR: '{query}' ===\n")
            
            if searched_queries:
                results.append(f"🔍 Searched business-relevant queries: {', '.join(searched_queries[:5])}\n")
            
            repositories = data.get("items", [])
            total_count = data.get("total_count", 0)
            
            if not repositories:
                return f"No repositories found for query: '{query}'"
            
            results.append(f"📊 Found {total_count} relevant business repositories, showing top {len(repositories)}:\n")
            
            for i, repo in enumerate(repositories, 1):
                # Extract repository information
                name = repo.get("name", "Unknown")
                full_name = repo.get("full_name", "Unknown")
                description = repo.get("description", "No description")
                html_url = repo.get("html_url", "")
                clone_url = repo.get("clone_url", "")
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)
                language = repo.get("language", "Unknown")
                updated_at = repo.get("updated_at", "Unknown")
                topics = repo.get("topics", [])
                
                # Format date
                if updated_at != "Unknown":
                    from datetime import datetime
                    try:
                        date_obj = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        updated_at = date_obj.strftime("%Y-%m-%d")
                    except:
                        pass
                
                results.append(f"{i}. 🔧 {name}")
                results.append(f"   👤 Owner: {full_name.split('/')[0] if '/' in full_name else 'Unknown'}")
                results.append(f"   📝 Description: {description}")
                results.append(f"   ⭐ Stars: {stars}")
                results.append(f"   🍴 Forks: {forks}")
                results.append(f"   💻 Language: {language}")
                results.append(f"   📅 Updated: {updated_at}")
                
                if topics:
                    results.append(f"   🏷️  Topics: {', '.join(topics[:5])}")
                
                results.append(f"   🔗 Repository: {html_url}")
                results.append(f"   📥 Clone: {clone_url}")
                results.append("")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"Error formatting repository results: {str(e)}")
            return f"Found repositories but failed to format details: {str(e)}"