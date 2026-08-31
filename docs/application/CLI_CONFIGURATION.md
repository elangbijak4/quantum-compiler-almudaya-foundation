# APPLICATION / PRODUCT LAYER — CLI CONFIGURATION SPECIFICATION

## Configuration Fields
- `default_backend`: Default backend identifier (`str`, default `"LOCAL_REFERENCE"`).
- `default_shots`: Default shot count (`int`, default `1000`).
- `output_format`: Output mode (`"human"` or `"json"`, default `"human"`).
- `seed_preference`: Optional random seed (`Optional[int]`, default `None`).
- `credential_ref`: Non-sensitive credential reference (`Optional[str]`, default `None`).

## Security Boundary
Raw API keys, secret tokens, or passwords MUST NOT be stored in `CLIConfig` files or serialized output.
