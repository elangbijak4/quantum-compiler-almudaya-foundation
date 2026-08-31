# MODULE 6 STAGE 8 — DEPENDENCY MAP

## 1. Upstream Module Dependencies (Read-Only)

- **Module 1**: `ClassicalAlgorithmSpec`
- **Module 2**: `ClassicalSemanticModel`, `QuantumCircuitIR`
- **Module 3**: `UTM`, `AML`
- **Module 4**: `LogicalGateType`, `QuantumCircuitIR`
- **Module 5**: Exact reversible compilation primitives

## 2. Stage 1–7 Dependencies (Read-Only)

- **Stage 1**: `ClassicalSemanticModel`
- **Stage 2**: `CompilerImageCharacterizer`
- **Stage 4**: `Stage4MultiLevelEquivalenceEvaluator` (Level 6 Equivalence)
- **Stage 6**: `EvolutionaryVocabularyState` ($GE(k)$)
- **Stage 7**: `EffectiveCompilationContext`, `Stage7CompilerResolver`
