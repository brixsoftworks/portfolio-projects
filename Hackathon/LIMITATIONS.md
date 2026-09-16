# Limitations

1. **Hardware Constraints**: The agentic loop requires multiple calls to the local LLM. Without a GPU, inference via `llama.cpp` on a standard CPU can take 30-60 seconds per file.
2. **Context Window**: Llama-3-8B has an 8K context window. Extremely large enterprise files might need chunking, which can degrade the Reviewer's ability to trace data flow perfectly.
3. **Zero-Day Discovery**: The system is highly capable of finding known vulnerability classes (OWASP Top 10) but may struggle to identify entirely novel exploit chains without explicit prompting.
