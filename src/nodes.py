import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import AgentState
from src.tools import search_web  
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
# --- LOAD ENVIRONMENT VARIABLES FIRST ---
load_dotenv()

# 1. Setup the Model (Gemini)
# We use a low temperature for more factual, less creative responses.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- NODE 1: THE STRATEGIST ---
def generate_strategy(state: AgentState):
    """
    Decides the next search query based on what we know so far.
    """
    print(f"--- STEP {state['iteration']}: GENERATING STRATEGY ---")
    
    # Analyze existing findings to determine what is missing
    findings_text = "\n".join(state.get('findings', []))
    
    prompt = f"""
    You are a Deep Research AI Agent. 
    Target: {state['original_query']}
    
    Current Findings:
    {findings_text}
    
    Based on the above, what is the SINGLE most important search query we need to run next 
    to uncover hidden connections, risks, or biographical details?
    Return ONLY the search query. No quotes.
    """
    
    # response = llm.invoke([HumanMessage(content=prompt)])
    response = AIMessage(content="Testing")
    # Update the state with the new query and increment the counter
    return {
        "current_query": response.content.strip(), 
        "iteration": state['iteration'] + 1
    }

# --- NODE 2: THE RESEARCHER ---
def conduct_research(state: AgentState):
    """
    Executes search and tracks visited domains.
    """
    query = state['current_query']
    # Get the list of domains we've already seen
    existing_domains = state.get('visited_domains', [])
    
    print(f"--- RESEARCHING: {query} ---")
    
    # Pass the domain list to the tool
    search_result = search_web(query, existing_domains)
    
    return {
        "latest_content": search_result["content"],
        # The state automatically appends these new domains to the main list
        "visited_domains": search_result["new_domains"]
    }

# --- NODE 3: THE ANALYST (Continued) ---
def analyze_findings(state: AgentState):
    """
    Extracts key facts and risks from the raw content.
    """
    raw_content = state['latest_content']
    
    prompt = f"""
    Analyze the following text for the target: {state['original_query']}
    
    Text:
    {raw_content}
    
    Extract high-value facts, potential risks, or hidden connections. 
    Ignore irrelevant info. 
    """
    
    # response = llm.invoke([HumanMessage(content=prompt)])
    response = AIMessage(content="Testing")
    # The result is added to our permanent 'findings' list
    return {"findings": [response.content]}