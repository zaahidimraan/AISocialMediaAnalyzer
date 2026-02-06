from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import generate_strategy, conduct_research, analyze_findings
from src.logger import get_logger

logger = get_logger("src.graph")


def should_continue(state: AgentState):
    if state['iteration'] < state['max_iterations']:
        logger.info(f"Deciding: Continue (Iteration {state['iteration']}/{MAX_ITERATIONS})")
        return "continue"
    logger.info("Deciding: Stop (Max iterations reached)")
    return "end"

logger.info("Building State Graph...")
workflow = StateGraph(AgentState)

workflow.add_node("strategist", generate_strategy)
workflow.add_node("researcher", conduct_research)
workflow.add_node("analyst", analyze_findings)

workflow.set_entry_point("strategist")
workflow.add_edge("strategist", "researcher")
workflow.add_edge("researcher", "analyst")

workflow.add_conditional_edges(
    "analyst",
    should_continue,
    {
        "continue": "strategist",
        "end": END
    }
)

app = workflow.compile()
logger.info("Graph compiled successfully.")