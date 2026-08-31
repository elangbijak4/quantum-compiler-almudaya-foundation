# MODULE 7 STAGE 4 — SCOPE DEFINITION

## 1. In-Scope Responsibilities

1. **Provider-Neutral Adapter Protocol (`CloudBackendAdapterProtocol`)**: Common abstraction for submitting, tracking, retrieving, and normalizing cloud quantum jobs across IBM, AWS, Google, Microsoft, and Mock targets.
2. **Pre-Submission Eligibility Validation**: Verifying that input native circuits carry `LoweringStatus.SEMANTICALLY_VERIFIED` and valid $C_{\text{backend}}$ native gate containment.
3. **Credential Privacy Enforcement**: Enforcing non-sensitive `credential_ref` handling (e.g. `env:IBM_TOKEN`) and preventing raw secret leakage in persistent logs or serialized results.
4. **Lifecycle State Management**: Tracking cloud job states (`CREATED`, `VALIDATED`, `SUBMITTED`, `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `EXPIRED`, `INCONCLUSIVE`).
5. **Provider Output Normalization**: Transforming provider-specific measurement payloads into `ProviderNeutralExecutionResult` with computational basis bitstring counts.

---

## 2. Explicit Out-of-Scope (Non-Scope)

1. **Production Cloud Job Execution During Initialization**: Zero real cloud job submissions during initialization (`CLOUD EXECUTION: 0%`, `HARDWARE EXECUTION: 0%`).
2. **Circuit Modification / Transpilation**: Stage 4 DOES NOT modify circuits or lower gate sets.
3. **Automatic Fallback / Re-lowering**: Stage 4 SHALL NOT substitute backends or invoke Module 6 recompilation upon failure.
4. **Statistical Result Verification**: Chi-squared testing and statistical equivalence belong exclusively to Stage 5.
