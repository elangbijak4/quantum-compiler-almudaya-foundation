# APPLICATION / PRODUCT LAYER — SCOPE BOUNDARY

## In Scope
- Application Contract API (`ApplicationContractProtocol`, `ApplicationContractService`).
- Request/Response data models (`ApplicationRequest`, `ApplicationResponse`).
- Application intent modeling (`COMPILE`, `INSPECT`, `SIMULATE`, `EXECUTE`, `VERIFY`, `LINEAGE`).
- Configuration and session boundaries for future CLI, GUI, Laboratory, and Explorer products.

## Out of Scope (Forbidden)
- Direct mutation of Core compiler source code or Core state.
- Redefining semantic equivalence (Module 4) or certification (Module 6).
- Production CLI executable implementations (argparse/click parsing).
- Production GUI framework implementations (PyQt/Electron/React).
- Live cloud provider credential loading or live cloud network submission.
