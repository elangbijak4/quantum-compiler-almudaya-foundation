# APPLICATION / PRODUCT LAYER — CLI / GUI SEPARATION

## Independent Consumer Architecture

1. **CLI Independence**:
   - The CLI is an independent product consumer.
   - Responsible for terminal command parsing (`--backend`, `--shots`, `--seed`), formatting output tables/text, and returning standard shell exit codes.
   - Communicates exclusively via `ApplicationContractService`.

2. **GUI Independence**:
   - The GUI is an independent product consumer.
   - Responsible for window management, visual circuit canvas rendering, probability distribution charts, and interactive shot count configuration panels.
   - Communicates exclusively via `ApplicationContractService`.

3. **No Inter-Product Dependency**:
   - CLI does NOT depend on GUI.
   - GUI does NOT depend on CLI.
   - Both products consume the identical underlying Application Contract.
