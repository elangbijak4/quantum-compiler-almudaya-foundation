# MODULE 7 STAGE 4 — ARCHITECTURE

```
+-----------------------------------------------------------------------------------+
|                            INPUT ARTIFACTS                                        |
|  [Verified LoweringResultArtifact] (M7 Stage 2) + [BackendCapabilityModel] (M7 S1)|
|  + [CloudExecutionRequest] (with credential_ref = "env:...")                      |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               MODULE 7 STAGE 4: CLOUD PROVIDER ADAPTER FRAMEWORK                  |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   | 1. Capability & Eligibility Pre-Submission Validation                     |   |
|   |    - Assert lowering_status == SEMANTICALLY_VERIFIED                      |   |
|   |    - Assert operations in native_gate_set & qubits in bounds              |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | 2. Provider Adapter Dispatch (IBM / AWS / Google / Microsoft / Mock)      |   |
|   |    - Implement CloudBackendAdapterProtocol                                |   |
|   |    - Secure credential resolution (read secret from env, never store)     |   |
|   |    - Submit job to remote cloud endpoint & obtain provider_job_id          |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | 3. Lifecycle Tracking & Result Normalization                              |   |
|   |    - Track status: SUBMITTED -> QUEUED -> RUNNING -> COMPLETED            |   |
|   |    - Normalize provider bitstrings into computational basis counts        |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               OUTPUT: ProviderNeutralExecutionResult                              |
| (Status: COMPLETED / FAILED / CANCELLED / EXPIRED / INCONCLUSIVE)                 |
+-----------------------------------------------------------------------------------+
```

---

## Architectural Invariants

1. **Provider-Neutral Interface**: All cloud adapters conform to `CloudBackendAdapterProtocol`.
2. **Credential Isolation**: Raw secrets NEVER enter request artifacts, job handles, serialized results, or provenance dictionaries.
3. **Derived Output**: Input native circuits are immutable; `ProviderNeutralExecutionResult` is a derived artifact.
