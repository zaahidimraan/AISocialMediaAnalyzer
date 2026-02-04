from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import generate_strategy, conduct_research, analyze_findings

# Configuration
MAX_ITERATIONS = 3

def should_continue(state: AgentState):
    """
    Determines if the agent should continue searching or stop.
    """
    if state['iteration'] < MAX_ITERATIONS:
        return "continue"
    return "end"

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("strategist", generate_strategy)
workflow.add_node("researcher", conduct_research)
workflow.add_node("analyst", analyze_findings)

# 3. Define Edges (The Flow)
# Start -> Strategist -> Researcher -> Analyst
workflow.set_entry_point("strategist")
workflow.add_edge("strategist", "researcher")
workflow.add_edge("researcher", "analyst")

# 4. Conditional Loop
# After the Analyst finishes, we check if we should loop back or stop
workflow.add_conditional_edges(
    "analyst",
    should_continue,
    {
        "continue": "strategist",
        "end": END
    }
)

# 5. Compile the Graph
app = workflow.compile()