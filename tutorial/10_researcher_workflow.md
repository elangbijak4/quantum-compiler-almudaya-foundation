# 10. Complete Researcher Workflow

End-to-end guide for conducting research experiments with the Quantum Compiler.

---

## Recommended 6-Step Research Methodology

1. **Step 1: Write Classical Algorithm**: Formulate the classical program (e.g. `tutorial/examples/03_expression.aml`).
2. **Step 2: Stepwise Transformation**: Run `aml` -> `utm` -> `rutm` -> `semantic` -> `map` -> `optimize` -> `lower`.
3. **Step 3: Inspect Intermediate Artifacts**: Use `inspect` to verify gate counts and topology mapping.
4. **Step 4: Execute Local Reference Simulation**: Run `simulate` with explicit shot count (`--shots 1000`) and seed (`--seed 42`).
5. **Step 5: Run Statistical Verification**: Execute `verify` to confirm state fidelity against reference distribution.
6. **Step 6: Capture Research Run Artifact**: Inspect `Output/Run_<timestamp>_<run_id>/manifest.json` and use recorded artifact hashes as peer-reviewed scientific proof.
