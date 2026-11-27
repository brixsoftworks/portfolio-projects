"""
search_and_speak.py

Direct pipeline: DuckDuckGo Search -> Direct Speech Output.
Zero LLM, zero Gemini API calls, zero token usage.
"""

from tools.web_search import web_search
from tools.tts_speaker import speak_text

def search_and_speak(query: str, max_speech_chars: int = 400):
    print("=" * 60)
    print(f" Searching DuckDuckGo: {query}")
    print("=" * 60)

    # 1. Fetch raw search results directly from DuckDuckGo
    results = web_search.invoke(query)
    
    print("\n Raw Search Output:")
    print("-" * 50)
    print(results)
    print("-" * 50)

    # 2. Feed output directly to the speech engine (No Gemini/LLM)
    print("\n Routing directly to Speech Model (edge-tts)...")
    speak_text(results, max_chars=max_speech_chars)
    print(" Completed speaking search result!\n")


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "latest weather update in Chennai today"
    search_and_speak(query)
