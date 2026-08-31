# APPLICATION / PRODUCT LAYER — CLI FOUNDATION & CONSTITUTION

## 1. Executive Summary & Core Freeze Invariant

The CLI Foundation is a dual-mode consumer (`Pipeline Mode` and `Stepwise / Inspection Mode`) residing strictly above the immutable **Application Contract** (`src/application/contract.py` / `src/application/service.py`).

### Fundamental Invariants:
1. **Core Freeze**: Modules 1–7 are 100% frozen. `CORE MUTATION = NONE`.
2. **Dual-Mode Architecture**: Supports Pipeline mode (`compile`) and Stepwise mode (`aml`, `utm`, `rutm`, `semantic`, `map`, `optimize`, `lower`, `simulate`, `execute`, `verify`, `lineage`, `inspect`).
3. **No Independent CLI Algorithms**: CLI delegates all transformation/computational requests to Core via Application Contract.
4. **CLI/GUI Symmetry**: CLI and GUI are peer consumers of the Application Contract.
5. **No Automatic Chain Expansion**: Stepwise commands execute strictly requested stages without auto-running downstream stages.

---

## 2. Constitutional Resolutions (Q1–Q40)

- **Q1: CLI as Compiler Interface**: RESOLVED — CLI exposes pipeline compilation (`compile`).
- **Q2: CLI as Computational Inspection Interface**: RESOLVED — CLI exposes read-only inspection (`inspect`, `lineage`).
- **Q3: Pipeline Mode**: RESOLVED — Orchestrates full pipeline while preserving stage transparency and artifact hashes.
- **Q4: Stepwise Mode**: RESOLVED — First-class stepwise commands (`aml`, `utm`, `rutm`, `semantic`, `map`, `optimize`, `lower`, `simulate`, `execute`, `verify`).
- **Q5: Command Categories**: RESOLVED — Categories: `TRANSFORMATION`, `EXECUTION`, `VALIDATION`, `INSPECTION`, `CONVENIENCE`.
- **Q6: Artifact Chaining**: RESOLVED — Explicit chaining via `parent_artifact_id`.
- **Q7: Artifact Identity**: RESOLVED — Exposes `artifact_id`, `artifact_type`, `parent_artifact_id`, `hash`, `status`, `provenance`.
- **Q8: Evidence Model**: RESOLVED — Separates `OUTPUT`, `EVIDENCE`, `CERTIFICATION`, `PROVENANCE`.
- **Q9: Certification Presentation**: RESOLVED — Displays genuine certificates iff issued by Module 4 authority.
- **Q10: Provenance Presentation**: RESOLVED — Read-only presentation of Stage 11 lineage history.
- **Q11: Inspection Semantics**: RESOLVED — Read-only inspection (`inspect`) without triggering side-effects.
- **Q12: Lineage Semantics**: RESOLVED — Visualizes Stage 11 historical lineage without mutation.
- **Q13: Explainability Boundary**: RESOLVED — Future `explain` capability specified without premature implementation.
- **Q14: Module Visibility**: RESOLVED — Exposes Module 1–7 stage attribution.
- **Q15: Laboratory Compatibility**: RESOLVED — Stepwise artifact model fully compatible with future Computational Laboratory GUI.
- **Q16: Application Contract Requirement**: RESOLVED — All stepwise operations invoke Application Contract APIs.
- **Q17: Explicit Action**: RESOLVED — Every transformation and execution command requires explicit user invocation.
- **Q18: No Automatic Chain Expansion**: RESOLVED — Stepwise commands do not auto-run downstream stages.
- **Q19: Stepwise Failure Semantics**: RESOLVED — Reports actual failure without auto-rerun or auto-fallback.
- **Q20: Output Model**: RESOLVED — Standardized output structure (`OPERATION`, `INPUT`, `OUTPUT`, `STATUS`, `EVIDENCE`).
- **Q21: Machine-Readable Output**: RESOLVED — Machine-readable JSON preserves full evidence and diagnostics.
- **Q22: Shot Semantics**: RESOLVED — `--shots N` applied only to sampling/simulation commands.
- **Q23: Backend Semantics**: RESOLVED — `--backend BACKEND_ID` applied only where backend selection is semantically valid.
- **Q24: Seed Semantics**: RESOLVED — `--seed N` passed through Application Contract.
- **Q25: Result Inspection**: RESOLVED — Inspects exact vs sampled probability distributions without conflation.
- **Q26: Authority Presentation**: RESOLVED — Identifies issuing Core module authority.
- **Q27: Diagnostic Role**: RESOLVED — Serves as diagnostic instrument for researchers and developers.
- **Q28: Research Role**: RESOLVED — Exposes intermediate IRs for educational and research inspection.
- **Q29: CLI/GUI Symmetry**: RESOLVED — CLI and GUI are peer consumers of `ApplicationContractProtocol`.
- **Q30: Core Freeze**: RESOLVED — Modules 1–7 remain 100% frozen.
- **Q31: Existing Foundation Compatibility**: RESOLVED — Compatible with `CLICommand`, `CLIExitCode`, `CLIConfig`, `CLIRequestAdapter`, `CLIResponseFormatter`.
- **Q32: Scope Boundary**: RESOLVED — Foundation clarification phase; production CLI executable deferred.
- **Q33: Future Product Extensibility**: RESOLVED — Extensible to Explorer, Agent, and API services.
- **Q34: Computational Truth vs Presentation**: RESOLVED — Presentation formatting does not alter computational evidence.
- **Q35: Mockability**: RESOLVED — Fully testable via `MockApplicationContractService`.
- **Q36: Security**: RESOLVED — Zero raw credential leakage.
- **Q37: Serialization**: RESOLVED — Clean separation of CLI presentation state and Core artifact truth.
- **Q38: Determinism**: RESOLVED — Deterministic request construction and exit code taxonomy.
- **Q39: Testability**: RESOLVED — Unit test suite in `tests/application/test_cli_foundation.py`.
- **Q40: Documentation Consistency**: RESOLVED — Consistent across all `docs/application/` documents.
