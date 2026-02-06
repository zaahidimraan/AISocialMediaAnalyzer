from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import (
    generate_strategy, 
    conduct_research, 
    extract_intelligence,  # Node 1 (The Detective)
    validate_and_assess,   # Node 2 (The Judge)
    write_report           # Node 3 (The Author)
)
from src.logger import get_logger

logger = get_logger("src.graph")

def should_continue(state: AgentState):
    """
    Decides whether to loop back for more research or go to the final report.
    """
    # 1. STOP if the Validator says we have enough info
    if state.get('is_complete'):
        logger.info("✅ Decision: COMPLETE -> Generating Report")
        return "report"

    # 2. STOP if we hit the max iteration limit
    if state['iteration'] >= state.get('max_iterations', 3):
        logger.info("🛑 Decision: MAX LIMIT REACHED -> Generating Report")
        return "report"

    # 3. CONTINUE if we still need info
    logger.info(f"🔄 Decision: LOOPING (Iteration {state['iteration']})")
    return "continue"

logger.info("Building State Graph...")
workflow = StateGraph(AgentState)

# --- ADD NODES ---
workflow.add_node("strategist", generate_strategy)
workflow.add_node("researcher", conduct_research)
workflow.add_node("extractor", extract_intelligence)
workflow.add_node("validator", validate_and_assess)
workflow.add_node("writer", write_report)  # <--- HERE IS THE REPORT NODE

# --- SET ENTRY POINT ---
workflow.set_entry_point("strategist")

# --- DEFINE EDGES (The Flow) ---
workflow.add_edge("strategist", "researcher")
workflow.add_edge("researcher", "extractor")
workflow.add_edge("extractor", "validator")

# --- CONDITIONAL EDGE ( The Decision) ---
# The Validator decides: Do we loop or write the report?
workflow.add_conditional_edges(
    "validator",          # From the Validator node...
    should_continue,      # ...run this logic function...
    {
        "continue": "strategist",  # If 'continue', go back to start
        "report": "writer"         # If 'report', go to WRITE REPORT
    }
)

# --- FINAL EDGE ---
# After writing the report, the agent stops.
workflow.add_edge("writer", END)

app = workflow.compile()
logger.info("Graph compiled successfully.")