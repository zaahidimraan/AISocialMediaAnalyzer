import os
from urllib.parse import urlparse
from langchain_community.tools.tavily_search import TavilySearchResults
from src.logger import get_logger, log_execution_time # <--- IMPORT

# Initialize Logger for this file
logger = get_logger("src.tools")

@log_execution_time(logger) # <--- Tracks time automatically
def search_web(query: str, visited_domains: list) -> dict:
    """
    Searches the web using Tavily, excluding previously visited domains.
    """
    # Log the input (Debug level)
    logger.debug(f"Searching for: '{query}' | Excluded domains: {len(visited_domains)}")

    if not os.getenv("TAVILY_API_KEY"):
        logger.critical("TAVILY_API_KEY missing from environment!")
        raise ValueError("TAVILY_API_KEY is missing from .env file")

    tool = TavilySearchResults(max_results=5)

    try:
        results = tool.invoke({
            "query": query, 
            "exclude_domains": visited_domains
        })
        
        formatted_output = ""
        new_domains = []
        
        for item in results:
            url = item['url']
            content = item['content']
            parsed_domain = urlparse(url).netloc.replace("www.", "")
            
            if parsed_domain not in visited_domains and parsed_domain not in new_domains:
                formatted_output += f"Source: {parsed_domain}\nContent: {content}\n\n"
                new_domains.append(parsed_domain)
            else:
                logger.debug(f"Skipping known source: {parsed_domain}")

        # Log success info
        logger.info(f"Search found {len(new_domains)} new unique sources.")
        
        return {
            "content": formatted_output,
            "new_domains": new_domains
        }

    except Exception as e:
        # The decorator handles the error logging, but we can add specific context if needed
        logger.error(f"Search failed: {e}")
        return {"content": f"Error performing search: {str(e)}", "new_domains": []}