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
    # model="gemini-3-flash-preview",
    model = "gemini-2.5-flash", 
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

@log_execution_time(logger)
def generate_strategy(state: AgentState):
    logger.info(f"--- STEP {state['iteration']}: Generating Strategy ---")
    
    findings_text = "\n".join(state.get('findings', []))
    
    prompt = f"""You are an expert intelligence analyst conducting deep research on: {state['original_query']}

                Search iteration: {str(state['iteration'])}/{str(state['max_iterations'])}

                Current Findings: {findings_text}

                Analyze the current findings and determine the SINGLE most strategic next search query that will:
                1. Fill critical information gaps
                2. Verify suspicious or inconsistent information
                3. Uncover hidden connections or risks
                4. Use specific names, companies, dates, or identifiers when available
                5. Combine multiple angles (e.g., "John Doe CFO Acme Corp 2015-2020")
                6. Focus on verifiable, public information sources
                7. Avoid redundant searches already covered
                8. Prioritize high-value, non-obvious connections

                Return ONLY the search query as a single line of text. No explanation, no preamble.
                """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        # response = AIMessage(content="Testing")
        # 1. Check if it's a list (Gemini 3 specific)
        if isinstance(response.content, list):
            # Extract text from all blocks that have type='text'
            final_text = "".join(
                block['text'] for block in response.content 
                if isinstance(block, dict) and block.get('type') == 'text'
            )
        else:
            # Fallback for older models (standard string)
            final_text = response.content
            
        # Remove quotes if the AI added them
        final_text = final_text.strip().replace('"', '')
        logger.debug(f"Strategy Generated: {response.content}")
        return {
            "current_query": final_text, 
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
def extract_intelligence(state: AgentState):
    try:
        logger.info("--- NODE: Extraction Analyst ---")
        raw_content = state.get('latest_content', "")
        
        if not raw_content:
            return {"raw_extraction": "No content found."}

        prompt = f"""
        You are a Data Extraction Specialist.
        TARGET: {state['original_query']}
        
        SOURCE DATA:
        {raw_content}
        
        EXISTING KNOWLEDGE:
        {state.get('findings', [])}
        
        ### MISSION
        Extract "Hard Data" and "Relational Links" from the RAW CONTENT. 
        Ignore marketing fluff, opinions, or generic website navigation.
        
        ### REQUIRED OUTPUT SECTIONS
        
        **SECTION 1: HARD FACTS (Atomic Claims)**
        Extract specific, verifiable data points. Group them by category:
        - [BIO]: Names, Aliases, DOB, Age, Nationality.
        - [CAREER]: Exact Job Titles, Dates of Tenure, Employer Names.
        - [FINANCE]: Asset values, Salary, Shareholdings, Transaction amounts.
        - [LEGAL]: Lawsuits, Case Numbers, Sanctions, Arrests.
        
        **SECTION 2: CONNECTION MAPPING (The Network Graph)**
        Trace relationships between entities.
        - Format: Entity A -> Relationship -> Entity B
        
        ### CONSTRAINTS
        1. PRECISION: Do not say "He is wealthy." Say "Net worth estimated at $50M by Forbes (2023)."
        2. RAW ONLY: Do not validate, score, or judge these facts yet. 
        3. NO DUPLICATES: If a fact is clearly in "EXISTING KNOWLEDGE", ignore it unless this source adds new details (like a specific date).
        
        Output strictly in the format above.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        # 1. Check if it's a list (Gemini 3 specific)
        if isinstance(response.content, list):
            # Extract text from all blocks that have type='text'
            final_text = "".join(
                block['text'] for block in response.content 
                if isinstance(block, dict) and block.get('type') == 'text'
            )
        else:
            # Fallback for older models (standard string)
            final_text = response.content
            
        # Remove quotes if the AI added them
        content = final_text.strip().replace('"', '')
        return {"raw_extraction": content}
    except Exception as e:
        logger.error(f"Error in extract_intelligence: {e}")
        {"raw_extraction": content}

@log_execution_time(logger)
def validate_and_assess(state: AgentState):
    try:
        logger.info("--- NODE: Risk & Validation Officer ---")
        
        new_claims = state.get('raw_extraction', "")
        existing_findings = state.get('findings', [])
        
        prompt = f"""
        You are a Senior Risk Officer.
        
        TARGET: {state['original_query']}
        NEW CLAIMS TO AUDIT:
        {new_claims}
        
        ### TASKS
        
        1. **Source Validation & Confidence Scoring**
        - Assign a Confidence Score (0-100%) to each new claim.
        - Logic: +20% if specific/verifiable, -50% if vague/anonymous.
        
        2. **Risk Pattern Recognition**
        - Scan for "Red Flags" (Fraud, Sanctions, PEP, Litigation, Conflicts).
        - Mark these clearly with [RISK-HIGH] or [RISK-MED].
        
        3. **Deduplication**
        - Compare with EXISTING KNOWLEDGE.
        - Tag as [NEW], [CORROBORATION], or [CONTRADICTION].
        
        ### OUTPUT FORMAT
        Return a bulleted list ready for the final database.
        Example:
        - [NEW][CONF: 90%] Subject is confirmed Director of Acme Corp (Source: Companies House).
        - [RISK-HIGH][CONF: 85%] Acme Corp was named in the 2021 Panama Papers leak.
        
        ### COMPLETENESS CHECK
        Do we have: Identity + Career + Financials + Risk Checks?
        Status: <COMPLETE or INCOMPLETE>
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        # 1. Check if it's a list (Gemini 3 specific)
        if isinstance(response.content, list):
            # Extract text from all blocks that have type='text'
            final_text = "".join(
                block['text'] for block in response.content 
                if isinstance(block, dict) and block.get('type') == 'text'
            )
        else:
            # Fallback for older models (standard string)
            final_text = response.content
            
        # Remove quotes if the AI added them
        content = final_text.strip().replace('"', '')
        
        # Parse status and content
        is_complete = "Status: COMPLETE" in content
        final_finding = content.replace("Status: COMPLETE", "").replace("Status: INCOMPLETE", "").strip()
        
        return {
            "findings": [final_finding], # Adds to the permanent list
            "is_complete": is_complete
        }
    except Exception as e:
        logger.error(f"Error in validate_and_assess: {e}")
        return {"findings": [], "is_complete": False}
    
@log_execution_time(logger)
def write_report(state: AgentState):
    logger.info("--- NODE: Report Writer ---")
    
    # 1. Gather all findings (which now include [CONFIDENCE] and [RISK] tags)
    all_findings = "\n".join(state.get('findings', []))
    
    prompt = f"""
    You are a Chief Risk Officer (CRO) finalizing a Due Diligence Report.
    
    TARGET: {state['original_query']}
    
    ### RAW INTELLIGENCE (Validated & Scored)
    {all_findings}
    
    ### MISSION
    Synthesize the raw intelligence into a final, professional Markdown report.
    
    ### STRICT REPORT STRUCTURE
    
    # 1. EXECUTIVE SUMMARY
    - Provide a "Bottom Line Up Front" (BLUF) assessment.
    - Assign an overall Risk Rating: [LOW / MEDIUM / HIGH / CRITICAL].
    - Justify the rating in 2-3 sentences.
    
    # 2. KEY RISK INDICATORS (The "Red Flags")
    - Isolate any finding tagged [RISK-HIGH] or [RISK-MED].
    - Present them as a bulleted list of warnings.
    - If no risks found, explicitly state: "No derogatory information identified."
    
    # 3. IDENTITY & BACKGROUND
    - Full Name, DOB/Age, Nationality (Verified?).
    - Career summary.
    
    # 4. FINANCIAL PROFILE
    - Sources of Wealth.
    - Corporate Assets & Affiliations.
    
    # 5. LEGAL ISSUES & CONTROVERSIES
    - Legal Cases, Sanctions, or Investigations
    - Public Controversies or Reputational Risks
    
    # 6. DATA RELIABILITY ASSESSMENT
    - Comment on the confidence scores (e.g., "Most facts verified by multiple sources" or "Data relies on single unverified source").
    
    ### STYLE RULES
    - Use professional, objective language (no "I think").
    - Cite the sources/confidence levels where relevant.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # --- Gemini 3 Text Extraction Logic ---
        if isinstance(response.content, list):
            report_text = "".join(
                block['text'] for block in response.content 
                if isinstance(block, dict) and block.get('type') == 'text'
            )
        else:
            report_text = response.content
            
        # Clean up any AI artifacts
        report_text = report_text.strip()
        
        logger.info(f"Report generated successfully ({len(report_text)} chars).")
        return {"final_report": report_text}
        
    except Exception as e:
        logger.error(f"Error writing report: {e}", exc_info=True)
        return {"final_report": f"Error generating report: {str(e)}"}