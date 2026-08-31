# MODULE 6 STAGE 8 — INTERFACE SPECIFICATIONS

## 1. Interface Definitions

### 1.1 `Stage8CircuitOptimizer.analyze_optimization_bounds`
```python
@classmethod
def analyze_optimization_bounds(
    cls,
    circuit: QuantumCircuitIR,
    context: EffectiveCompilationContext,
    model: Optional[ClassicalSemanticModel] = None,
) -> OptimizationCostReport: ...
```
- **Inputs**: `QuantumCircuitIR`, `EffectiveCompilationContext`, optional `ClassicalSemanticModel`.
- **Outputs**: `OptimizationCostReport`.
- **Preconditions**: `context.configuration_status == "FEASIBLE"`.
- **Invariants**: `Q_opt` must contain only gates in `context.effective_vocabulary`.

### 1.2 `CircuitCostEvaluator.evaluate_cost`
```python
@classmethod
def evaluate_cost(cls, circuit: QuantumCircuitIR) -> CircuitCostMetrics: ...
```
- **Inputs**: `QuantumCircuitIR`.
- **Outputs**: `CircuitCostMetrics`.

### 1.3 `serialize_optimization_report` / `deserialize_optimization_report`
```python
def serialize_optimization_report(report: OptimizationCostReport) -> str: ...
def deserialize_optimization_report(json_str: str) -> OptimizationCostReport: ...
```
- **Guarantees**: Canonical JSON formatting, key sorting, round-trip equality (`deserialize(serialize(R)) == R`).
