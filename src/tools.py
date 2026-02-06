import os
from langchain_tavily import TavilySearch

def search_web(query: str, visited_urls: list) -> dict:
    """
    Searches the web, filters out previously visited URLs, and returns
    both the content string and the list of new URLs found.
    """
    # 1. Check for API Key
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is missing from .env file")

    # 2. Initialize the tool
    tool = TavilySearch(max_results=5)

    try:
        # 3. Execute Search
        results = tool.invoke({"query": query})
        
        formatted_output = ""
        new_urls = []
        
        # 4. Filter and Format
        for item in results:
            url = item['url']
            
            # CRITICAL CHECK: Only process if we haven't seen this URL before
            if url not in visited_urls:
                formatted_output += f"Source: {url}\nContent: {item['content']}\n\n"
                new_urls.append(url)
            else:
                print(f"Skipping known source: {url}")
            
        return {
            "content": formatted_output,
            "new_urls": new_urls
        }

    except Exception as e:
        return {"content": f"Error performing search: {str(e)}", "new_urls": []}