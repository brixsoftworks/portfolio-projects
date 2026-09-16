# Model Strategy

## Local Large Language Model (LLM)
- **Model**: Llama-3-8B-Instruct (Quantized to 4-bit GGUF).
- **Why**: Fits in <8GB VRAM, allowing it to run entirely locally on standard hackathon/developer hardware.
- **Inference**: Handled via `llama.cpp` for maximum CPU/GPU efficiency.

## Proprietary Component (False-Positive Filter)
- **Model**: DistilBERT
- **Why**: LLM inference is slow. By fine-tuning a small classification model on static analysis alerts and their code context, we can instantly drop 80% of files that contain no real vulnerabilities, reserving the slow LLM exclusively for high-risk code.
