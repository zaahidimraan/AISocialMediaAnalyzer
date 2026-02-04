from src.graph import app
import os

def run_agent(target_name: str):
    print(f"Starting Deep Research on: {target_name}...\n")
    
    # Initialize the state
    initial_state = {
        "original_query": target_name,
        "current_query": "",
        "iteration": 0,
        "findings": [],
        "visited_urls": [],
        "latest_content": ""
    }

    # Run the graph
    # thread_id is used for checkpointing (memory), optional here but good practice
    result = app.invoke(initial_state)

    print("\n\n========== FINAL REPORT ==========")
    print(f"Target: {result['original_query']}")
    print("\nFindings:")
    for i, finding in enumerate(result['findings']):
        print(f"{i+1}. {finding}\n")

if __name__ == "__main__":
    # You can change this name to test different targets
    TARGET = "Elon Musk" 
    run_agent(TARGET)