import os
import json
import time
from llm_orchestrator import run_llm
from builder import build_site, rebuild_site
from executor import execute_python_code
from search_tool import search_web

MAX_API_CALLS = 100
WAIT_TIME_SECONDS = 300 # 5 minutes

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def read_state():
    ensure_dir("logs")
    state_path = os.path.join("logs", "state.json")
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "api_calls": 0,
        "grid": [["" for _ in range(5)] for _ in range(5)], # 5x5 grid (Breadth=5, Depth=5)
        "current_depth": 0,
        "current_breadth": 0,
        "consecutive_high_scores": 0,
        "history": []
    }

def write_state(state):
    ensure_dir("logs")
    state_path = os.path.join("logs", "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def generate_react_prompt(question, text_content, state):
    prompt = f"""You are an Agentic Autoresearcher. Use the provided extracted text to answer the user's question.

User Question: {question}

State Context:
You are at Depth={state['current_depth']}, Breadth={state['current_breadth']} in your research grid.

Extracted Text:
{text_content}

Your goal is to Reason and Act (ReAct).
First, REASON: Think about what information is missing and how to get it (Search, Code, or synthesize).
Second, ACT: Provide a plan.
If you need to execute code, format it as:
```python
# your code
```
If you need to search the web, format it as:
SEARCH: "your query"

Finally, provide a Confidence Score from 1-10 on your current understanding.
Format your output EXACTLY like this:
REASON: <your thoughts>
PLAN: <your plan>
[optional code or search action]
SCORE: <number between 1 and 10>
"""
    return prompt

def extract_action(llm_response):
    code = None
    search_query = None
    score = 0

    # Extract code block if present
    if "```python" in llm_response:
        parts = llm_response.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0].strip()

    # Extract search query
    for line in llm_response.split('\n'):
        if line.startswith("SEARCH:"):
            search_query = line.replace("SEARCH:", "").strip().strip('"')
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except ValueError:
                pass

    return code, search_query, score

def update_grid(state, reasoning):
    d = state["current_depth"]
    b = state["current_breadth"]

    if d < 5 and b < 5:
        state["grid"][d][b] = reasoning

    # Simple traversal: move breadth first, then depth
    state["current_breadth"] += 1
    if state["current_breadth"] >= 5:
        state["current_breadth"] = 0
        state["current_depth"] += 1

    return state

def human_approval(plan_text):
    print("\n" + "="*50)
    print("RESEARCH PLAN PROPOSED BY AGENT:")
    print(plan_text)
    print("="*50)
    while True:
        choice = input("Approve this action? (Y/N): ").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("Please enter Y or N.")

def run_agent_loop(initial_text, question, model_choice):
    state = read_state()
    current_context = initial_text

    while True:
        if state["api_calls"] >= MAX_API_CALLS:
            print(f"Stopping: Reached maximum API calls ({MAX_API_CALLS}).")
            break

        if state["consecutive_high_scores"] >= 3:
            print("Stopping: Reached high confidence (Score >= 8) for 3 consecutive iterations.")
            break

        prompt = generate_react_prompt(question, current_context, state)
        print(f"\n--- Iteration {state['api_calls'] + 1} ---")
        llm_response = run_llm(prompt, question, model_choice) # Pass both args required by llm_orchestrator
        state["api_calls"] += 1

        # Save thought process
        code, search_query, score = extract_action(llm_response)

        iteration_log = {
            "iteration": state["api_calls"],
            "response": llm_response,
            "code_executed": code,
            "search_query": search_query,
            "score": score
        }
        state["history"].append(iteration_log)

        # Update stop conditions
        if score >= 8:
            state["consecutive_high_scores"] += 1
        else:
            state["consecutive_high_scores"] = 0

        state = update_grid(state, llm_response[:100] + "...") # brief summary in grid

        # Rebuild site to show audit trail
        build_site("Final answer will be populated here.", json.dumps(state, indent=2))
        rebuild_site()
        write_state(state)

        if code or search_query:
            if human_approval(llm_response):
                if code:
                    print("Executing code...")
                    stdout, stderr, rcode = execute_python_code(code)
                    current_context += f"\n\n--- Code Execution Result ---\nSTDOUT: {stdout}\nSTDERR: {stderr}\n"

                if search_query:
                    print(f"Executing search: {search_query}...")
                    search_results = search_web(search_query)
                    current_context += f"\n\n--- Search Results ---\n{search_results}\n"
            else:
                print("Action rejected by user. Asking agent to replan.")
                current_context += "\n\nUser rejected the proposed plan. Please reason and plan a different approach without executing that specific code or search."
        else:
            print("No action proposed. Synthesizing.")

        if state["consecutive_high_scores"] >= 3 or state["api_calls"] >= MAX_API_CALLS:
            continue

        print(f"Waiting for {WAIT_TIME_SECONDS} seconds before next iteration...")
        time.sleep(WAIT_TIME_SECONDS)

    # Final Synthesis
    print("\nGenerating final answer...")
    final_prompt = f"Synthesize all your findings into a comprehensive markdown answer for the user's question: {question}\n\nContext:\n{current_context}"
    final_answer = run_llm(final_prompt, question, model_choice)
    build_site(final_answer, json.dumps(state, indent=2))
    rebuild_site()

    return final_answer
