"""
tools/web_search.py

LangChain web search tool using DuckDuckGo.
Free, no API key required.
"""

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import tool


# ── DuckDuckGo wrapper (controls how many results come back) ──────────────────
_wrapper = DuckDuckGoSearchAPIWrapper(
    max_results=8,          # return up to 8 search results
    region="in-en",         # India/English results (change to "wt-wt" for global)
    safesearch="off",
    time=None,              # all time
)

# ── Raw LangChain tool (used by the agent later) ──────────────────────────────
search = DuckDuckGoSearchRun(api_wrapper=_wrapper)


# ── Standalone helper (easy to call directly in scripts) ──────────────────────
@tool
def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo and return a summary of the top results.
    Use this when you need current information, news, facts, or anything
    that requires looking up online.

    Args:
        query: The search query string.

    Returns:
        A text summary of the top search results.
    """
    try:
        results = search.run(query)
        return results if results else "No results found for that query."
    except Exception as e:
        return f"Search failed: {str(e)}"


# ── Quick standalone test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    test_query = "latest AI news today"
    print(f"\n Searching: '{test_query}'\n")
    print(web_search.invoke(test_query))

