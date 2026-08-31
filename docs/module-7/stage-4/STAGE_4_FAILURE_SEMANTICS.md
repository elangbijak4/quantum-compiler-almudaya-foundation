# MODULE 7 STAGE 4 — FAILURE SEMANTICS & TAXONOMY

## 1. Stage 4 Failure Classifications

1. `BACKEND_UNSUPPORTED`: Selected provider or backend ID is not supported by installed adapters.
2. `BACKEND_CAPABILITY_MISMATCH`: Circuit qubit count, depth, or operations exceed provider backend capability.
3. `SUBMISSION_FAILURE`: Network timeout, HTTP error, or provider API error during job submission.
4. `QUEUE_FAILURE`: Job dropped, expired, or cancelled while waiting in provider execution queue.
5. `EXECUTION_FAILURE`: Physical hardware or cloud simulator execution error on provider side.
6. `RESULT_RETRIEVAL_FAILURE`: Provider returned malformed, unparseable, or empty measurement payload.
7. `AUTHENTICATION_FAILURE`: Provider authentication failed due to invalid, expired, or missing credentials.
8. `CREDENTIAL_FAILURE`: Non-sensitive credential reference (`credential_ref`) could not be resolved from environment or secure manager.
9. `PROVIDER_UNAVAILABLE`: External provider cloud API or endpoint is unreachable.
10. `INCONCLUSIVE`: Execution status or payload returned indeterminate state.

---

## 2. Recovery Policy

- Failures produce structured `ProviderNeutralExecutionResult` with status `FAILED` or `INCONCLUSIVE`.
- Failures SHALL NOT alter upstream state, switch backends automatically, or trigger recompilation.
