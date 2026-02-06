from flask import Flask, render_template, request
from src.graph import app as graph_app  # Import your LangGraph agent
from dotenv import load_dotenv

# Load env variables
load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    report = None
    target_name = None
    
    if request.method == 'POST':
        target_name = request.form.get('target_name')
        if target_name:
            print(f"Received request for: {target_name}")
            
            # 1. Setup the initial state for your agent
            initial_state = {
                "original_query": target_name,
                "current_query": "",
                "iteration": 0,
                "findings": [],
                "visited_urls": [],
                "latest_content": ""
            }
            
            # 2. Run the Agent (Synchronously)
            # Note: For a production app, this should be done in a background task (like Celery)
            # because it might take 10-20 seconds to finish.
            try:
                result = graph_app.invoke(initial_state)
                report = result.get('findings', [])
            except Exception as e:
                report = [f"Error occurred: {str(e)}"]

    return render_template('index.html', report=report, target=target_name)

if __name__ == '__main__':
    # Debug=True allows the server to auto-reload when you change code
    app.run(debug=True, port=5000)