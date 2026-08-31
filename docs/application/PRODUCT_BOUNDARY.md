# APPLICATION / PRODUCT LAYER — PRODUCT BOUNDARY

## Core Principle: "THE CORE MUST NOT KNOW THE PRODUCT"

1. **Isolation Invariant**: Core Modules 1–7 contain zero imports or references to `src/application/`, CLI modules, GUI modules, or web servers.
2. **Product Extensibility**: A new product (e.g. `QuantumNotebook`, `QuantumAgent`) can be added by connecting to `ApplicationContractService` without modifying a single line of Core code.
3. **No Authority Redistribution**: Products cannot override semantic equivalence (Module 4), circuit governance (Module 6), or backend capabilities ($C_{\text{backend}}$).
