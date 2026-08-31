# MODULE 6 STAGE 9 — INTERFACE SPECIFICATIONS

## 1. Interface Definitions

### 1.1 `ResourceQualityEvaluator.extract_resource_profile`
```python
@classmethod
def extract_resource_profile(cls, circuit: QuantumCircuitIR) -> ResourceProfile: ...
```
- **Inputs**: `QuantumCircuitIR`.
- **Outputs**: `ResourceProfile`.

### 1.2 `ResourceQualityEvaluator.evaluate_quality_profile`
```python
@classmethod
def evaluate_quality_profile(
    cls,
    circuit: QuantumCircuitIR,
    optimization_report: Optional[OptimizationCostReport] = None,
    semantic_equivalent: bool = True,
    feasibility_status: str = "FEASIBLE",
) -> QualityProfile: ...
```
- **Inputs**: `QuantumCircuitIR`, optional `OptimizationCostReport`, boolean `semantic_equivalent`, string `feasibility_status`.
- **Outputs**: `QualityProfile`.

### 1.3 `ParetoTradeOffAnalyzer.compare_candidates`
```python
@classmethod
def compare_candidates(
    cls,
    candidate_a_id: str,
    profile_a: QualityProfile,
    candidate_b_id: str,
    profile_b: QualityProfile,
) -> ComparisonResult: ...
```
- **Inputs**: Candidate IDs and corresponding `QualityProfile` instances.
- **Outputs**: `ComparisonResult`.

### 1.4 `serialize_quality_profile` / `deserialize_quality_profile`
```python
def serialize_quality_profile(profile: QualityProfile) -> str: ...
def deserialize_quality_profile(json_str: str) -> QualityProfile: ...
```
- **Guarantees**: Canonical JSON formatting, key sorting, round-trip equality (`deserialize(serialize(P)) == P`).
