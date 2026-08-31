# APPLICATION / PRODUCT LAYER — CLI ARCHITECTURE DEFINITION

## Architectural Hierarchy

```
        +-------------------------------------------------------+
        |                 CLI Frontends / Commands              |
        |   Pipeline Mode (compile)  |  Stepwise Mode (aml...)  |
        +---------------------------+---------------------------+
                                    |
                                    v
        +-------------------------------------------------------+
        |            CLI Foundation Abstractions                |
        |  CLIRequestAdapter, CLIResponseFormatter, CLIConfig   |
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

## CLI / GUI Symmetry
The CLI and GUI are peer consumers of the Application Contract. Neither is a dependency of the other.
