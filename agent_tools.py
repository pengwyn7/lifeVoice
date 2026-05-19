import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from duckduckgo_search import DDGS
from datetime import datetime
from utils.groq_client import query

load_dotenv()

# Define tools
@tool
def web_search(query: str) -> str:
    """Search the web for current information using DuckDuckGo. Useful for questions about current events, facts, or trends not in your existing knowledge."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No search results found."
            formatted = "\n\n".join([
                f"Result {i+1}:\nTitle: {r['title']}\nSnippet: {r['body']}"
                for i, r in enumerate(results)
            ])
            return formatted
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def get_current_datetime() -> str:
    """Get the current date and time. Useful for time-related questions or when you need to know what day/time it is now."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S (local time)")

@tool
def calculator(expression: str) -> str:
    """Calculate simple math expressions (e.g., '2+2', '10*5', '100/4')."""
    try:
        safe_chars = set("0123456789+-*/(). ")
        if not all(c in safe_chars for c in expression):
            return "Invalid expression - only numbers and basic operators (+-*/) allowed."
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

# List of all tools
tools = [web_search, get_current_datetime, calculator]

def run_agent(user_input: str, persona_context: str, chat_history: list | None = None) -> str:
    """Run the agent with the given user input and persona context."""
    try:
        # Check if tools are needed
        tool_prompt = f"""{persona_context}

User question: {user_input}

Decide if you need to use any tools:
- Use web_search if the question is about current events, recent facts, or something not in your knowledge
- Use get_current_datetime if the question asks for current date/time
- Use calculator if it's a simple math question
- If no tools are needed, just answer directly

If you need a tool, specify which one and the input. If multiple tools, list them. If none, just answer."""

        # First, get decision from LLM
        decision = query(tool_prompt, "You are a helpful assistant that decides if tools are needed.")
        
        # Check which tools are mentioned
        tool_results = []
        for tool in tools:
            if tool.name.lower() in decision.lower():
                # Extract query for the tool if needed
                if tool.name == "web_search":
                    # Use the original user input as search query
                    tool_result = web_search.invoke(user_input)
                    tool_results.append(f"Web search results:\n{tool_result}")
                elif tool.name == "get_current_datetime":
                    tool_result = get_current_datetime.invoke({})
                    tool_results.append(f"Current date/time: {tool_result}")
                elif tool.name == "calculator":
                    # Try to extract expression from user input
                    tool_result = calculator.invoke(user_input)
                    tool_results.append(f"Calculator result: {tool_result}")
        
        # Combine everything into final prompt
        final_prompt = f"""{persona_context}

User question: {user_input}

{'Useful information from tools:\n' + '\n\n'.join(tool_results) if tool_results else ''}

Please answer the user's question in character."""
        
        # Get final answer
        return query(final_prompt, persona_context)
    except Exception as e:
        return f"Sorry, I had trouble processing that. {str(e)}"
