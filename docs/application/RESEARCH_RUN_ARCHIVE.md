# APPLICATION / PRODUCT LAYER — RESEARCH RUN / OUTPUT ARCHIVE ARCHITECTURE SPECIFICATION

## 1. Executive Summary & Fundamental Invariants

The **Output / Research Run Archive** (`src/application/archive/`) provides a persistent, researcher-facing materialization of executed compiler runs without modifying or weakening the frozen Quantum Compiler Core (Modules 1–7).

### Fundamental Invariants:
1. **Research-Facing Materialization**: The Output Archive is NOT a computational authority. All authoritative results originate from frozen Core Module authorities.
2. **Core Freeze**: Modules 1–7 are 100% frozen. `CORE MUTATION = NONE`.
3. **Run Immutability**: Finalized `ResearchRun` folders (`Output/Run_<timestamp>_<run_id>/`) are strictly read-only and append-only. No retrospective rewrite of historical runs.
4. **Artifact Identity & Chain Preservation**: Archived artifacts retain authoritative `artifact_id`, `artifact_type`, `parent_artifact_id`, `hash`, `status`, and `provenance`.
5. **Security & Credential Isolation**: Zero raw secret tokens stored in manifests (`manifest.json`) or reports (`README.md`).

---

## 2. Directory & Manifest Structure

```text
Output/
  └── Run_<YYYYMMDD_HHMMSS>_<run_id>/
      ├── manifest.json   (Canonical JSON manifest with SHA-256 digest)
      └── README.md       (Human-readable Markdown research report)
```

### Manifest Schema (`manifest.json`):
- `run_id`: Authoritative run identifier (`str`).
- `created_at`: UTC ISO-8601 timestamp (`str`).
- `status`: Completion status (`"COMPLETED"`, `"PARTIAL"`, `"FAILED"`).
- `backend_id`: Target backend identifier (`str`).
- `shots`: Execution shot count (`int`).
- `verification_policy_id`: Verification policy ID (`str`).
- `artifacts_count`: Number of archived stage artifacts (`int`).
- `artifacts`: List of stage artifact objects (`artifact_id`, `artifact_type`, `parent_artifact_id`, `hash`, `stage`, `status`, `provenance`).
- `lineage_reference`: Stage 11 historical lineage reference (`Optional[str]`).
- `manifest_hash`: 64-character SHA-256 digest of canonical JSON.
