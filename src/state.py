import operator
from typing import Annotated, List, TypedDict

class AgentState(TypedDict):
    original_query: str                   # The initial name/entity provided by the user
    current_query: str                    # The specific search query for the current step
    iteration: int                        # Counter to prevent infinite loops
    findings: Annotated[List[str], operator.add]  # Accumulates facts found over time
    visited_urls: Annotated[List[str], operator.add] # Tracks sources to avoid duplicates
    visited_domains: Annotated[List[str], operator.add]