# APPLICATION / PRODUCT LAYER — CLI CONTRACT BINDING

## Contract Binding Architecture

The CLI Foundation binds to the Application Contract via two primary helper classes in `src/application/cli/model.py`:

```
   CLI Command Line / Arguments
               │
               ▼
      CLIRequestAdapter
               │ (builds ApplicationRequest)
               ▼
  ApplicationContractProtocol / Service
               │ (returns ApplicationResponse)
               ▼
     CLIResponseFormatter
               │ (determines CLIExitCode & renders output)
               ▼
     Terminal Exit / JSON Output
```

### Precedence Resolution:
1. **Explicit Command Argument** (e.g. `--shots 500`)
2. **CLI Config Setting** (e.g. `default_shots = 1000`)
3. **Default Policy** (`shots = 1000`)
