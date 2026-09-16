# Evaluation

We measure the success of Sentinel-Local using four key metrics:

1. **False Positive Reduction Rate (FPRR)**: The percentage of non-exploitable static analysis alerts successfully discarded by our proprietary FPF model and the Verifier Agent.
2. **True Positive Rate (TPR)**: How many actual vulnerabilities the Reviewer Agent successfully flags.
3. **Latency**: Average time (in seconds) taken to process a single repository file.
4. **Hallucination Rate**: How often the Reviewer Agent hallucinates a bug, and whether the Verifier Agent correctly catches it.
