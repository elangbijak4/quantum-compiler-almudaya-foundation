# APPLICATION / PRODUCT LAYER — CLI COMMAND MODEL

## Authorized Command Taxonomy

### 1. Convenience Pipeline Command
- `compile`: Orchestrates full pipeline while exposing all intermediate stage artifacts and hashes.

### 2. Stepwise Transformation Commands
- `aml`: Classical algorithm -> AML transformation.
- `utm`: AML -> Universal Turing Machine IR.
- `rutm`: UTM -> Reversible UTM IR.
- `semantic`: Reversible synthesis & semantic certification.
- `map`: Qubit mapping & topology physicalization.
- `optimize`: Pareto quality optimization & rewrite rules.
- `lower`: Logical-to-native gate lowering.

### 3. Execution Commands
- `simulate`: Local reference simulator execution.
- `execute`: Cloud/hardware provider job submission.

### 4. Validation Commands
- `verify`: Statistical verification (Hellinger & KS metrics).

### 5. Read-Only Inspection Commands
- `inspect`: Read-only inspection of artifacts & capabilities.
- `lineage`: Historical provenance chain visualization.
