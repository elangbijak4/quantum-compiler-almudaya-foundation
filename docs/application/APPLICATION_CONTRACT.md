# APPLICATION / PRODUCT LAYER — CONTRACT SPECIFICATIONS

## 1. Request Data Model (`ApplicationRequest`)
- `request_id`: Unique request identifier (`str`).
- `intent`: Operational intent (`ApplicationIntent`).
- `source_code`: Classical input source (`Optional[str]`).
- `logical_circuit_id`: Target logical circuit reference (`Optional[str]`).
- `native_circuit_id`: Target native circuit reference (`Optional[str]`).
- `backend_id`: Target backend identifier (`str`).
- `provider_id`: Target provider identifier (`str`).
- `shots`: Configurable execution shot count (`int`).
- `seed`: Optional random seed (`Optional[int]`).
- `credential_ref`: Non-sensitive credential reference (`Optional[str]`).
- `verification_policy_id`: Verification policy reference (`str`).
- `request_hash`: Canonical SHA-256 hash (`str`).

## 2. Response Data Model (`ApplicationResponse`)
- `request_id`: Originating request identifier (`str`).
- `intent`: Executed operational intent (`ApplicationIntent`).
- `status`: Completion status (`ApplicationStatus`).
- `error_code`: Failure code if applicable (`Optional[str]`).
- `error_message`: Human-readable error message (`Optional[str]`).
- `artifact_references`: Map of output artifact IDs (`Dict[str, str]`).
- `result_payload`: Normalized output result (`Dict[str, Any]`).
- `diagnostics`: Application diagnostics (`Dict[str, Any]`).
- `response_hash`: Canonical SHA-256 hash (`str`).
