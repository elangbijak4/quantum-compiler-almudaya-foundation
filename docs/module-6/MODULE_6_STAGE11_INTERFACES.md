# MODULE 6 STAGE 11 INTERFACES

## 1. Primary Public Interfaces

### `analyze_stage11_lineage`
- **Module Path**: `src.module6.analysis.stage11`
- **Input**:
  - `audit_report`: `GovernanceAuditReport`
- **Output**: `LineageTraceReport`
- **Preconditions**: `audit_report` must be a valid Stage 10 report.
- **Postconditions**: Returns deterministic `LineageTraceReport` preserving upstream hashes.
- **Determinism**: 100% deterministic (no unseeded randomness or unmanaged system clock dependency).
- **Side-Effects**: Zero. Does not mutate input audit reports or upstream objects.

---

## 2. Model Interfaces

### `HistoricalLineageRecord`
- **Properties**: `record_id`, `algorithm_id`, `audit_id`, `certificate_id`, `provenance_chain_hash`, `timestamp_identity`.
- **Methods**: `to_dict() -> Dict[str, Any]`

### `LineageTraceReport`
- **Properties**: `trace_id`, `algorithm_id`, `records`, `provenance`, `report_hash`.
- **Methods**: `to_dict() -> Dict[str, Any]`
