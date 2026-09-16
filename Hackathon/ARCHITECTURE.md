# Sentinel-Local Architecture

## The Pipeline
1. **Application UI**: Streamlit interface taking repository path.
2. **False-Positive Filter**: A proprietary DistilBERT model that acts as an intelligent gatekeeper, discarding up to 80% of static analysis noise.
3. **Planner Agent**: A Llama-3-8B instance that receives the filtered list of files and constructs an audit strategy.
4. **Reviewer Agent**: Deeply analyzes a specific file using the LLM to understand data flow and logic.
5. **Verifier Agent (Critic)**: Takes the output from the Reviewer and independently attempts to construct a logical proof. If it fails, the vulnerability is discarded.
