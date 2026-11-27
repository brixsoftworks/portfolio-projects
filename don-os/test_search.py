"""
test_search.py

Quick test to verify the DuckDuckGo web search tool is working.
Run with:  python test_search.py
"""

from tools.web_search import web_search

QUERIES = [
    "What is the latest iPhone model?",
    "Python 3.13 new features",
    "weather in Chennai today",
]

if __name__ == "__main__":
    print("=" * 60)
    print("  Web Search Tool Test — DuckDuckGo + LangChain")
    print("=" * 60)

    for query in QUERIES:
        print(f"\n Query: {query}")
        print("-" * 50)
        result = web_search.invoke(query)
        print(result)
        print()

    print("=" * 60)
    print("  All tests done!")
    print("=" * 60)

