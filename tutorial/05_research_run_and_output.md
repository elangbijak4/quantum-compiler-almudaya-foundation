# 05. Research Run & Output Archive

Learn how completed compiler runs are materialized into persistent, immutable research records.

---

## Directory Organization

All completed or partial runs are stored under `Output/`:

```text
Output/
  └── Run_<timestamp>_<run_id>/
      ├── manifest.json   (Canonical JSON manifest with SHA-256 hash)
      └── README.md       (Human-readable Markdown research report)
```

---

## The Manifest (`manifest.json`)

The manifest captures full reproducible computational metadata:
- `run_id`: Authoritative run ID.
- `created_at`: UTC ISO-8601 timestamp string.
- `status`: Completion status (`COMPLETED`, `PARTIAL`, `FAILED`).
- `backend_id`: Target backend identifier.
- `shots`: Shot count configured.
- `artifacts`: Inventory of all stage artifacts with parent linkage and hashes.
- `manifest_hash`: 64-character SHA-256 digest of the manifest itself.

---

## Historical Run Immutability Invariant

> **Rule**: Once a `ResearchRun` directory is finalized, its recorded files and hashes are strictly immutable. Executing subsequent runs (e.g. `Run_B`) will NEVER mutate or rewrite previous runs (e.g. `Run_A`).
