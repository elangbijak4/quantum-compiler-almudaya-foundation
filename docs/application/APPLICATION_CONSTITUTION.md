# APPLICATION / PRODUCT LAYER CONSTITUTION — GOVERNANCE FOUNDATION & CONTRACT ARCHITECTURE

## 1. Governance Principles & Fundamental Axiom

The Application / Product Layer resides strictly above the frozen **Quantum Compiler + Execution Core** (Modules 1–7).

### Fundamental Axiom:
> **"THE CORE MUST NOT KNOW THE PRODUCT."**

The Core MUST NOT depend on or contain CLI, GUI, Laboratory, Explorer, Notebook, Agent, or Web/Mobile product logic. Products interact with the Core strictly through the immutable `ApplicationContractService`.

```
                    ┌─────────────────────────┐
                    │      CLI / GUI / UI     │
                    │   (Product Experience)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Application Contract  │
                    │ (Request/Response API)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   QUANTUM COMPILER CORE │
                    │     (Modules 1 – 7)     │
                    └─────────────────────────┘
```

---

## 2. Constitutional Resolutions (Q1–Q45)

### Q1: Core / Product Boundary
Modules 1–7 constitute the frozen Quantum Compiler + Execution Core. The Application Layer is a consumer residing strictly above the Core.

### Q2: Product Independence
The Application Layer supports multiple independent consumers (CLI, GUI, Laboratory, Explorer, Notebook, Agent) through a single stable `ApplicationContractProtocol`.

### Q3: Application Contract
The contract operates on explicit `ApplicationRequest` and `ApplicationResponse` payloads, avoiding exposure of mutable internal Core objects.

### Q4: Request / Response Model
Immutable dataclasses holding user parameters (`ApplicationRequest`) and standard completion status/results (`ApplicationResponse`).

### Q5: Authority Preservation
The Application Layer has ZERO authority over semantic equivalence (Mod 4), logical governance (Mod 6), lowering (Stage 2), simulation (Stage 3), provider adapters (Stage 4), statistical verification (Stage 5), or historical lineage (Stage 11).

### Q6: Artifact Ownership
Products reference immutable Core artifacts via stable IDs and SHA-256 hashes (`logical_circuit_id`, `native_circuit_id`, `execution_id`, `verification_id`).

### Q7: Immutability
Products MUST NOT mutate Core artifacts in place.

### Q8: Lineage Visibility
Lineage can be visually or textually inspected without modifying Stage 11 append-only history.

### Q9–Q12: Product Independence (CLI, GUI, Laboratory, Explorer)
Each product is an independent consumer operating through the Application Contract.

### Q13: Shot Configuration
Preserves user-configurable shot count (`shots: int = 1000`) passed via `ApplicationRequest`.

### Q14: Backend Selection
Discovers backends via Stage 1 Backend Registry without inventing a competing backend registry.

### Q15: Simulation / Execution Distinction
Clearly distinguishes `LOCAL_SIMULATION`, `MOCK_EXECUTION`, and `CLOUD_HARDWARE_EXECUTION`.

### Q16–Q18: Result, Verification & Failure Presentation
Consumes normalized Core results (`ProviderNeutralExecutionResult`, `StatisticalVerificationRecord`) and Core failure taxonomy (`BACKEND_CAPABILITY_MISMATCH`, `SUBMISSION_FAILURE`, `EXECUTION_FAILURE`, `INCONCLUSIVE`).

### Q19: Credential Boundary
Zero raw API keys, tokens, or passwords stored in application state or logs. Non-sensitive `credential_ref` (e.g. `"env:IBM_QUANTUM_TOKEN"`) only.

### Q20–Q22: Configuration, Session & Workspace Boundaries
UI session and workspace state are kept completely separate from Core artifacts and Stage 11 lineage.

### Q23–Q27: Serialization, Versioning, Security, Determinism
Independent versioning (`application_contract_version = "1.0.0"`). Deterministic SHA-256 hashing.

### Q28–Q30: Hidden Invocation & User Action Boundaries
Operations must correspond to explicit user actions. No hidden auto-recompilation, auto-relowering, or auto-reruns.

### Q31–Q45: Testability, Extensibility, Observability & Data Ownership
Product extensibility via Application Contract. Dependency direction strictly `Products -> Application Contract -> Core`.
