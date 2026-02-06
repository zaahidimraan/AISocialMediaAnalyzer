import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from src.tools import search_web
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.logger import get_logger, log_execution_time 

load_dotenv()
logger = get_logger("src.nodes")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

@log_execution_time(logger)
def generate_strategy(state: AgentState):
    logger.info(f"--- STEP {state['iteration']}: Generating Strategy ---")
    
    findings_text = "\n".join(state.get('findings', []))
    
    prompt = f"""
    You are a Deep Research AI Agent. Target: {state['original_query']}
    Current Findings: {findings_text}
    Based on the above, what is the SINGLE most important search query next?
    Return ONLY the search query.
    """
    
    try:
        # response = llm.invoke([HumanMessage(content=prompt)])
        response = AIMessage(content="Testing")
        logger.debug(f"Strategy Generated: {response.content}")
        return {
            "current_query": response.content.strip(), 
            "iteration": state['iteration'] + 1
        }
    except Exception as e:
        logger.error("Error in generate_strategy", exc_info=True)
        raise e

@log_execution_time(logger)
def conduct_research(state: AgentState):
    query = state['current_query']
    existing_domains = state.get('visited_domains', [])
    
    logger.info(f"--- Researching: {query} ---")
    
    search_result = search_web(query, existing_domains)
    
    return {
        "latest_content": search_result["content"],
        "visited_urls": search_result["new_urls"]
    }

@log_execution_time(logger)
def analyze_findings(state: AgentState):
    logger.info("--- Analyzing Findings ---")
    raw_content = state['latest_content']
    
    if not raw_content:
        logger.warning("No content found to analyze.")
        return {"findings": []}

    prompt = f"""
    Analyze the following text for target: {state['original_query']}
    Text: {raw_content}
    Extract high-value facts, risks, or connections.
    """
    
    try:
        # response = llm.invoke([HumanMessage(content=prompt)])
        response = AIMessage(content="Testing")
        logger.debug(f"Analysis complete. Length: {len(response.content)} chars")
        return {"findings": [response.content]}
    except Exception as e:
        logger.error("Error in analyze_findings", exc_info=True)
        raise e