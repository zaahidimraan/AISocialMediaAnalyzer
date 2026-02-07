import operator
from typing import Annotated, List, TypedDict

class AgentState(TypedDict):
    original_query: str                   # The initial name/entity provided by the user
    current_query: str                    # The specific search query for the current step
    iteration: int                        # Counter to prevent infinite loops
    findings: Annotated[List[str], operator.add]  # Accumulates facts found over time
    visited_urls: Annotated[List[str], operator.add] # Tracks sources to avoid duplicates
    visited_domains: Annotated[List[str], operator.add] # Stored the visit domain
    latest_content: str # Stored the latest search results
    max_iterations: int      # Controls how many loops the agent runs
    max_search_results: int  # Controls how many links Tavily fetches
    is_complete: bool  # True = Stop searching, False = Keep going
    raw_extraction: str # Temporary field for Node A
    final_report : str # Stored the final report