# MODULE 6 STAGE 8 — ARCHITECTURE & COMPONENT SPECIFICATION

## 1. Architectural Overview

Stage 8 introduces `Stage8CircuitOptimizer` in `src/module6/optimization/`.

```
                        +------------------------------------+
                        |  EffectiveCompilationContext (S7)  |
                        +------------------------------------+
                                          |
                                          v
+-----------------------+     +-------------------------------+     +-----------------------------------+
| QuantumCircuitIR (S2) | --> | Stage8CircuitOptimizer (S8)   | --> | Level 6 Semantic Verifier (S4)   |
+-----------------------+     +-------------------------------+     +-----------------------------------+
                                          |
                                          v
                              +-------------------------------+
                              | OptimizationCostReport (S8)   |
                              +-------------------------------+
```

---

## 2. Component Breakdown

1. **`CircuitCostMetrics` (`src/module6/optimization/model.py`)**:
   Dataclass holding `total_gate_count`, `gate_counts_by_type`, `circuit_depth`, `t_gate_depth`, `cnot_depth`, `qubit_count`.
2. **`CircuitCostEvaluator` (`src/module6/optimization/metrics.py`)**:
   Computes exact cost metrics for `QuantumCircuitIR`.
3. **`CanonicalRewriteRules` (`src/module6/optimization/rules.py`)**:
   Defines semantics-preserving rewrite transformations under $G_{\text{effective}}$.
4. **`OptimizationProvenanceGenerator` (`src/module6/optimization/provenance.py`)**:
   Generates deterministic provenance records.
5. **`OptimizationCostReport` (`src/module6/optimization/model.py`)**:
   Immutable output report.
6. **`Stage8CircuitOptimizer` (`src/module6/optimization/optimizer.py`)**:
   Master analytical orchestrator.
