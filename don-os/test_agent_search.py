import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.web_search import web_search

load_dotenv()

def test_agent_with_search():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] Error: GEMINI_API_KEY not found in .env")
        return

    # Use the current Gemini 3.8 Flash model
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        google_api_key=api_key,
        temperature=0.3
    )

    # Bind the DuckDuckGo search tool to the model
    llm_with_tools = llm.bind_tools([web_search])

    query = "What is the latest score or status of the most recent Formula 1 or cricket match?"
    print(f"\n User Prompt: {query}")
    print("=" * 60)

    # Step 1: Model decides if it needs the tool
    response = llm_with_tools.invoke(query)

    if response.tool_calls:
        print(f" LLM decided to invoke tool: {response.tool_calls[0]['name']}")
        print(f" Arguments: {response.tool_calls[0]['args']}")
        
        # Step 2: Execute tool
        tool_args = response.tool_calls[0]['args']
        tool_result = web_search.invoke(tool_args)
        print(f"\n Search Snippet (First 200 chars):\n{str(tool_result)[:200]}...\n")
        
        # Step 3: Send back tool response to LLM for final answer
        messages = [
            {"role": "user", "content": query},
            response,
            {"role": "tool", "tool_call_id": response.tool_calls[0]["id"], "content": str(tool_result)}
        ]
        final_answer = llm.invoke(messages)
        print(" Agent Final Answer:")
        print("-" * 60)
        
        # Extract text safely whether content is str or list of dict blocks
        text_output = ""
        if isinstance(final_answer.content, list):
            for part in final_answer.content:
                if isinstance(part, dict) and "text" in part:
                    text_output += part["text"]
                elif hasattr(part, "text"):
                    text_output += part.text
        elif isinstance(final_answer.content, str):
            text_output = final_answer.content

        print(text_output if text_output else final_answer.content)
    else:
        print(" LLM answered directly without tool calls:")
        print(response.content)

if __name__ == "__main__":
    test_agent_with_search()

