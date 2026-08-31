# MODULE 7 STAGE 1 — TEST PLAN

## 1. Test Suite Organization & Status: COMPLETE (24 PASS)

- `tests/module7/test_module7_initialization.py`: Baseline initialization tests (3 PASS).
- `tests/module7/test_stage1_registry.py`: Stage 1 production engine tests (21 PASS).

---

## 2. Test Coverage & Verification Evidence

1. **Backend Identity & Hashing**: Verified 64-char SHA-256 `capability_hash` determinism (`test_01`).
2. **Multi-Backend Provider Identity**: Verified multiple backends per provider (`test_02`).
3. **Capability Inspection**: Verified `supports_gate`, `supports_qubits`, `supports_shots` (`test_03`).
4. **Registry Operations**: Tested `register_backend`, `get_backend`, `contains_backend`, `get_by_hash` (`test_04`).
5. **Multi-Version Preservation**: Verified versioned snapshot storage under `(backend_id, capability_version)` (`test_05`).
6. **Retirement Mechanics**: Verified `retire_backend` deactivates backend while preserving historical queryability (`test_06`).
7. **Canonical Serialization & Roundtrip**: Verified `deserialize(serialize(X)) == X` (`test_07`).
8. **Snapshot Immutability**: Verified `FrozenInstanceError` when attempting field mutation (`test_08`).
9. **Credential Privacy & Security Negative Test**: Verified raw secrets NEVER appear in serialized capability payload (`test_09`).
10. **No Hidden Gate Expansion**: Verified registering new native gates DOES NOT mutate Module 6 $GE(k)$ or $B_u$ (`test_10`).
11. **Negative Validation Tests**: 11 explicit negative validation cases covering empty IDs, unsupported types, invalid qubit counts, max shots, empty gate sets, topology self-loops, out-of-bounds qubits, duplicate topology edges, version conflict re-registration, and corrupted capability hash detection (`test_11` .. `test_21`).
