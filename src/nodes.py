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
    
    # prompt = f"""
    # You are a Deep Research AI Agent. Target: {state['original_query']}
    # Current Findings: {findings_text}
    # Based on the above, what is the SINGLE most important search query next?
    # Return ONLY the search query.
    # """
    prompt = f"""You are an expert intelligence analyst conducting deep research on: {state['original_query']}

                Search iteration: {str(state['iteration'])}/{str(state['max_iterations'])}

                Current Findings: {findings_text}

                Analyze the current findings and determine the SINGLE most strategic next search query that will:
                1. Fill critical information gaps
                2. Verify suspicious or inconsistent information
                3. Uncover hidden connections or risks
                4. Build upon previous discoveries
                5. Use specific names, companies, dates, or identifiers when available
                6. Combine multiple angles (e.g., "John Doe CFO Acme Corp 2015-2020")
                7. Focus on verifiable, public information sources
                8. Avoid redundant searches already covered
                9. Prioritize high-value, non-obvious connections

                Return ONLY the search query as a single line of text. No explanation, no preamble.
                """
    
    try:
        # response = llm.invoke([HumanMessage(content=prompt)])
        response = AIMessage(content="Testing")
        print(response.content)
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
    
    search_result = search_web(query, existing_domains,state["max_search_results"])
    
    return {
        "latest_content": search_result["content"],
        "visited_urls": search_result["new_urls"]
    }

@log_execution_time(logger)
def analyze_findings(state: AgentState):
    logger.info("--- Analyzing Findings ---")
    raw_content = state.get('latest_content', "")
    
    if not raw_content:
        return {"findings": [], "is_complete": False}

    # prompt = f"""
    # You are a Research Analyst.
    # Target: {state['original_query']}
    
    # Existing Findings:
    # {state.get('findings', [])}
    
    # New Content to Analyze:
    # {raw_content}
    
    # 1. Extract new key high-value facts, risks, or connections from the "New Content".
    # 2. Assess if we have enough information to write a comprehensive biography/report.
    
    # Format your response exactly like this:
    # Findings: <your extracted facts here>
    # Status: <COMPLETE or INCOMPLETE>
    # """
    
    prompt = f"""
        You are a Senior Intelligence Analyst performing a Due Diligence investigation.
        
        TARGET: {state['original_query']}
        
        CONTEXT
        1. ALREADY KNOWN (Do not repeat these):
        {state.get('findings', [])}
        
        2. NEW SOURCE DATA (Analyze this for *new* info):
        {raw_content}
        
        INSTRUCTIONS
        
        TASK A: EXTRACT NEW INTELLIGENCE
        Scan the "NEW SOURCE DATA" for high-value facts that are NOT in "ALREADY KNOWN".
        - Focus on: Verifiable Identity, Career History, Financial Assets, Legal Issues, and adverse media.
        - CRITICAL: If the text is irrelevant (ads, cookies, navigation), output "No new relevant information found."
        - CRITICAL: Do not summarize the article. Extract specific atomic facts (e.g., "Subject is Board Member of X Corp").
        
        TASK B: EVALUATE COMPLETENESS
        Determine if we have enough to build a comprehensive profile.
        
        Mark status as COMPLETE ONLY if we meet ALL criteria below:
        1. Identity Verified (Full Name + Age/DOB or Nationality).
        2. Primary Income Source Identified (Current Job or Business).
        3. Risk Check Performed (We have actively looked for and noted any legal issues or controversies).
        
        If ANY of these are missing or vague, mark **INCOMPLETE**.
        
        REQUIRED OUTPUT FORMAT
        Findings: <Bulleted list of NEW facts>
        Status: <COMPLETE or INCOMPLETE>
        """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # Simple parsing logic
        is_complete = "Status: COMPLETE" in content
        
        # Clean up the text (remove the status line for the final report)
        clean_findings = content.replace("Status: COMPLETE", "").replace("Status: INCOMPLETE", "").strip()
        
        if is_complete:
            logger.info("✅ Analyst decided sufficient information has been gathered.")
        
        return {
            "findings": [clean_findings], 
            "is_complete": is_complete # <--- This updates the state
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_findings: {e}")
        return {"findings": [], "is_complete": False}