# APPLICATION / PRODUCT LAYER — CLI ARTIFACT CHAINING MODEL

## Explicit Artifact Chain

```text
source:<id>
    ↓
aml:<id>
    ↓
utm:<id>
    ↓
rutm:<id>
    ↓
certificate:<id>
    ↓
circuit:<id>
    ↓
optimized:<id>
    ↓
native:<id>
    ↓
execution:<id>
    ↓
result:<id>
    ↓
verification:<id>
```

## Chaining Semantics
- Stepwise commands accept previous artifact IDs (e.g. `parent_artifact_id`).
- Artifact identity parameters:
  - `artifact_id`: Unique identifier.
  - `artifact_type`: Artifact classification.
  - `parent_artifact_id`: Predecessor artifact reference.
  - `hash`: 64-character SHA-256 digest.
  - `status`: Completion status.
  - `provenance`: Historical lineage reference.
