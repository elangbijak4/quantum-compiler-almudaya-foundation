# APPLICATION / PRODUCT LAYER — ARCHITECTURE DEFINITION

## Component Hierarchy

```
        +-------------------------------------------------------+
        |                 CLI / GUI / Frontends                 |
        |   Pipeline Mode (compile)  |  Stepwise Mode (aml...)  |
        +---------------------------+---------------------------+
                                    |
                                    v
        +-------------------------------------------------------+
        |            CLI Foundation & Output Archive            |
        |  CLIRequestAdapter, CLIResponseFormatter, CLIConfig   |
        |            OutputArchiveManager, ResearchRun          |
        +---------------------------+---------------------------+
                                    |
                                    v
        +-------------------------------------------------------+
        |                Application Contract                   |
        |    ApplicationContractService (src/application/)      |
        +---------------------------+---------------------------+
                                    |
                                    v
        +-------------------------------------------------------+
        |       FROZEN QUANTUM COMPILER CORE (Modules 1 – 7)    |
        +-------------------------------------------------------+
```

## Two-Layer Record Model
1. **Authoritative Computational Record**: Module 4 (Semantic Certificates), Module 6 Stage 11 (Persistent Lineage), Module 7 (Execution & Verification Records).
2. **Researcher-Facing Output Record**: Materialized historical run archives (`Output/Run_<timestamp>_<run_id>/manifest.json`) capturing the exact executed pipeline without claiming computational authority.
