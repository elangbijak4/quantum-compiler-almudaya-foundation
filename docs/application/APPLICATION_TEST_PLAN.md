# APPLICATION / PRODUCT LAYER — TEST PLAN

## Test Inventory
1. **Initialization Tests**: Verify scaffold imports, request/response models, SHA-256 request/response hashing, and contract service dispatch (`test_application_initialization.py`).
2. **Contract Intent Tests**: Verify `compile`, `inspect`, `simulate`, `execute`, `verify`, and `lineage` API methods.
3. **Security & Credential Isolation Tests**: Verify zero raw secrets leak in requests, responses, or logs.
4. **Core Immutability Tests**: Verify application operations DO NOT mutate Core artifacts or Stage 11 lineage.
