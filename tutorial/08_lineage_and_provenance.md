# 08. Provenance & Lineage Inspection

Guide to inspecting read-only artifact properties and Stage 11 historical lineage.

---

## Read-Only Inspection Commands

### 1. Artifact & Backend Inspection
```bash
python -m src.application.cli.main inspect LOCAL_REFERENCE
```

### 2. Historical Lineage Inspection
```bash
python -m src.application.cli.main lineage LOG_CIRC_DEFAULT
```

---

## Read-Only Invariant

> **Rule**: `inspect` and `lineage` commands are strictly read-only lookup operations. Calling `inspect` or `lineage` will NEVER trigger recompilation, simulation, execution, or lineage mutation.
