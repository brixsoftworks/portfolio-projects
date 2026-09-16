# Sentinel-Local

**Offline Agentic AI Security Auditor (hackathon prototype)**

Sentinel-Local is an air-gapped security auditor concept: analyze Python/JS
codebases with static analysis, filter noise with a trained classifier, and
have a local LLM verify findings — without sending code to external APIs.

> **⚠️ Honest status: working prototype with a stubbed core.**
> This was built for a hackathon. The docs below separate what is real from
> what is demo theater.

## What is actually implemented

- **Bandit static analysis** — real subprocess integration; findings feed the
  pipeline.
- **False-positive filter (FPF)** — a genuinely trained CodeBERT/RoBERTa
  classifier (`src/models/`): training loop with AdamW, warmup, gradient
  clipping, checkpointing. Trained on ~200 rows of *handwritten template*
  data (see caveats in `DATASET.md`) — treat its accuracy claims as
  unmeasured.
- **RAG engine + orchestrator scaffolding** — ChromaDB context retrieval and
  pydantic-schema'd agent plumbing are real code paths.
- **Streamlit dashboard UI** — renders pipeline events end-to-end.

## What is STUBBED (returns canned output)

- **The multi-agent LLM loop (Planner / Reviewer / Verifier).** The local
  Llama-3-8B integration described in `MODEL.md` was never implemented:
  "real" mode returns *"Not implemented."*, the llama.cpp import is commented
  out, and demo runs replay hardcoded JSON with artificial thinking delays.
- `tests/` and `demo_repo/` are empty despite earlier doc claims.
- No `requirements.txt`/`pyproject.toml` — the environment is not reproducible.
- Metrics named in `EVALUATION.md` were never computed (including the
  "80% FP reduction" claim).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install bandit streamlit chromadb sentence-transformers torch transformers pydantic
```

## Running the UI

```bash
streamlit run src/ui/app.py
```

## If you want to finish it

1. Wire a real llama.cpp/GGUF backend behind the existing agent wrappers.
2. Replace template-generated FPF training data with labeled real data.
3. Add the dependency manifest + tests, then re-run EVALUATION.md honestly.
