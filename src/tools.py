import os
from langchain_community.tools.tavily_search import TavilySearchResults

def search_web(query: str) -> str:
    """
    Searches the web using Tavily API and returns the results as a string.
    """
    # 1. Check for API Key
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is missing from .env file")

    # 2. Initialize the tool
    # max_results=5 gives us a good breadth of information for "Deep Research"
    tool = TavilySearchResults(max_results=5)

    # 3. Execute Search
    # The tool returns a list of dictionaries: [{'url': '...', 'content': '...'}]
    try:
        results = tool.invoke({"query": query})
        
        # 4. Format the output
        # We join the results into a string so the Analyst node can read it naturally.
        formatted_output = ""
        for item in results:
            formatted_output += f"Source: {item['url']}\nContent: {item['content']}\n\n"
            
        return formatted_output

    except Exception as e:
        return f"Error performing search: {str(e)}"