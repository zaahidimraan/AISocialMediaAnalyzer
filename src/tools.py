import os
from urllib.parse import urlparse
from langchain_community.tools.tavily_search import TavilySearchResults

def search_web(query: str, visited_domains: list) -> dict:
    """
    Searches the web using Tavily, excluding previously visited domains.
    Returns content and a list of NEW domains found.
    """
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is missing from .env file")

    # 1. Initialize tool
    tool = TavilySearchResults(max_results=5)

    try:
        # 2. Execute Search with exclude_domains
        # We can pass the list directly since it's already clean domains
        results = tool.invoke({
            "query": query, 
            "exclude_domains": visited_domains
        })
        
        formatted_output = ""
        new_domains = []
        
        # 3. Process Results
        for item in results:
            url = item['url']
            content = item['content']
            
            # Extract domain (e.g., "https://www.bbc.com/..." -> "bbc.com")
            parsed_domain = urlparse(url).netloc.replace("www.", "")
            
            # Double-check: ensure we don't add the same domain twice in this single batch
            if parsed_domain not in visited_domains and parsed_domain not in new_domains:
                formatted_output += f"Source: {parsed_domain}\nContent: {content}\n\n"
                new_domains.append(parsed_domain)
            
        return {
            "content": formatted_output,
            "new_domains": new_domains
        }

    except Exception as e:
        return {"content": f"Error performing search: {str(e)}", "new_domains": []}