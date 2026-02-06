import os
from urllib.parse import urlparse
from langchain_community.tools.tavily_search import TavilySearchResults
from src.logger import get_logger, log_execution_time

logger = get_logger("src.tools")

@log_execution_time(logger)
def search_web(query: str, visited_urls: list, state: AgentState):
    """
    Searches using Tavily. Allows same domain but blocks exact visited URLs.
    """
    logger.debug(f"Searching for: '{query}' | Visited URLs count: {len(visited_urls)}")

    if not os.getenv("TAVILY_API_KEY"):
        logger.critical("TAVILY_API_KEY missing!")
        raise ValueError("TAVILY_API_KEY is missing from .env file")

    # 1. Initialize tool WITHOUT exclude_domains
    # We want to see results from 'wikipedia.org' even if we've been there before,
    # just not the *same page*.
    tool = TavilySearchResults(state["max_search_results"])

    try:
        results = tool.invoke({"query": query})
        
        formatted_output = ""
        new_urls = []
        
        # 2. Filter AFTER results come back
        for item in results:
            url = item['url']
            content = item['content']
            
            # CRITICAL CHANGE: Check if this specific URL is in our history
            if url not in visited_urls:
                # Optional: Clean source name for the LLM (visual only)
                parsed_domain = urlparse(url).netloc.replace("www.", "")
                
                formatted_output += f"Source: {parsed_domain}\nURL: {url}\nContent: {content}\n\n"
                new_urls.append(url)
            else:
                logger.debug(f"Skipping known URL: {url}")

        logger.info(f"Search found {len(new_urls)} new unique URLs.")
        
        return {
            "content": formatted_output,
            "new_urls": new_urls
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"content": f"Error: {str(e)}", "new_urls": []}