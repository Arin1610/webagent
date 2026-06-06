import os
from groq import Groq
from dotenv import load_dotenv
from agent.tools import search_web, scrape_webpage

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a helpful AI research agent. You have access to two tools:

1. web_search(query) - Search the web for information
2. scrape_webpage(url) - Read the full content of a webpage

To use a tool, respond in this EXACT format:
THOUGHT: [your reasoning about what to do next]
ACTION: tool_name
INPUT: your input to the tool

When you have enough information to answer, respond in this EXACT format:
THOUGHT: I now have enough information to answer
FINAL ANSWER: [your comprehensive answer with sources]

Rules:
- Always think before acting
- Use web_search first, then scrape specific pages for more detail
- Always include sources in your final answer
- Maximum 5 tool calls per question
"""

def run_agent(question: str, max_iterations: int = 5) -> dict:
    """Run the ReAct agent on a question."""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {question}"}
    ]
    
    steps = []
    
    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})
        
        print(f"\n--- Step {i+1} ---")
        print(content)
        
        # Check if agent is done
        if "FINAL ANSWER:" in content:
            final_answer = content.split("FINAL ANSWER:")[1].strip()
            steps.append({"step": i+1, "type": "final", "content": content})
            return {
                "question": question,
                "answer": final_answer,
                "steps": steps,
                "total_steps": i+1
            }
        
        # Parse tool call
        if "ACTION:" in content and "INPUT:" in content:
            try:
                action = content.split("ACTION:")[1].split("\n")[0].strip()
                input_text = content.split("INPUT:")[1].split("\n")[0].strip()
                
                # Execute tool
                if action == "web_search":
                    tool_result = search_web(input_text)
                elif action == "scrape_webpage":
                    tool_result = scrape_webpage(input_text)
                else:
                    tool_result = f"Unknown tool: {action}"
                
                steps.append({
                    "step": i+1,
                    "type": "tool_call",
                    "action": action,
                    "input": input_text,
                    "result": tool_result[:500],
                    "content": content
                })
                
                # Add tool result to messages
                messages.append({
                    "role": "user",
                    "content": f"OBSERVATION: {tool_result[:2000]}"
                })
                
            except Exception as e:
                messages.append({
                    "role": "user", 
                    "content": f"OBSERVATION: Tool execution failed — {e}"
                })
        
    return {
        "question": question,
        "answer": "Agent did not reach a final answer within the iteration limit.",
        "steps": steps,
        "total_steps": max_iterations
    }


if __name__ == "__main__":
    result = run_agent("What are the latest developments in AI agents in 2025?")
    print(f"\n=== FINAL ANSWER ===")
    print(result["answer"])
    print(f"\nCompleted in {result['total_steps']} steps")