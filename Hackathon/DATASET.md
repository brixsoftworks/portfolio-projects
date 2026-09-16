# Dataset Strategy

## Origin
Our proprietary False-Positive Filter (FPF) was trained on a combination of:
1. **Synthetic Data**: Generated templates mimicking common true and false positive static analysis alerts.
2. **Juliet Test Suite**: (C/C++/Java/Python) Known vulnerable and patched file pairs.
3. **CVEfixes**: Historical CVEs mapped to their commit hashes.

## Processing
Data was processed into a format of `(Alert Message, Code Context) -> Label (1 for True Positive, 0 for False Positive)`.

## Leakage Prevention
A strict 10% test set is completely held out during all training runs and only used for the final benchmark script.
