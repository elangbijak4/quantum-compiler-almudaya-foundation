# MODULE 7 STAGE 1 — FAILURE SEMANTICS & TAXONOMY

## 1. Stage 1 Failure Classifications

1. `BACKEND_NOT_FOUND`: Target `backend_id` is not registered in the registry.
2. `BACKEND_IDENTITY_INVALID`: Malformed or empty `backend_id` or `provider_id`.
3. `CAPABILITY_INVALID`: Malformed capability descriptor (e.g. qubit count <= 0 or empty native gate set).
4. `CAPABILITY_VERSION_INVALID`: Unsupported or incompatible `capability_version`.
5. `BACKEND_UNSUPPORTED`: Backend descriptor violates provider-neutral contract.
6. `CAPABILITY_MISMATCH`: Preliminary check shows logical circuit parameters exceed target device limits.
7. `REGISTRY_INTEGRITY_FAILURE`: Registry snapshot or capability hash verification fails.

---

## 2. Recovery & Boundary Policy

- Stage 1 failures produce explicit structured error results without mutating registered state or upstream Module 6 state.
