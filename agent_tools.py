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
        # First, proactively check if we should use tools (simple heuristics + LLM)
        tool_results = []
        user_input_lower = user_input.lower()
        
        # Simple heuristics to decide tool usage
        use_web = False
        use_time = False
        use_calc = False
        
        # Time keywords
        time_keywords = ["what time", "current time", "today's date", "what day", "current date"]
        use_time = any(keyword in user_input_lower for keyword in time_keywords)
        
        # Calculator keywords
        calc_keywords = ["calculate", "what is", "how much", "+", "-", "*", "/", "times", "plus", "minus", "divided by"]
        use_calc = any(keyword in user_input_lower for keyword in calc_keywords)
        
        # Web search - if not time or calc, and it's a factual question
        use_web = not (use_time or use_calc)
        
        # Use web search if it's a question about a person, event, etc.
        web_indicators = ["who is", "what is", "where is", "when did", "why is", "how did", "news about", "trending", "latest", "current", "right now"]
        if any(indicator in user_input_lower for indicator in web_indicators):
            use_web = True
        
        # Execute tools
        if use_web:
            tool_result = web_search.invoke(user_input)
            tool_results.append(f"Web search results:\n{tool_result}")
        
        if use_time:
            tool_result = get_current_datetime.invoke({})
            tool_results.append(f"Current date/time: {tool_result}")
        
        if use_calc:
            try:
                tool_result = calculator.invoke(user_input)
                tool_results.append(f"Calculator result: {tool_result}")
            except:
                pass
        
        # Combine everything into final prompt
        final_prompt = f"""{persona_context}

User question: {user_input}

{'Useful information from tools:\n' + '\n\n'.join(tool_results) if tool_results else ''}

Please answer the user's question in character."""
        
        # Get final answer
        return query(user_input, final_prompt, chat_history)
    except Exception as e:
        return f"Sorry, I had trouble processing that. {str(e)}"
