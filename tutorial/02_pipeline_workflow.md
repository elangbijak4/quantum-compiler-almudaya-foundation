# 02. Pipeline Workflow Mode

Pipeline Mode provides convenience one-shot orchestration for end-to-end compilation.

---

## Conceptual Architecture

```text
Classical Source -> AML -> UTM -> RUTM -> Semantic Certificate -> Logical Circuit -> Native Circuit -> Execution/Simulation -> Verification
```

Unlike Stepwise Mode, `compile` automatically passes artifacts down the complete authorized compiler chain.

---

## Command Syntax

```bash
python -m src.application.cli.main compile <input> [--backend BACKEND_ID] [--shots N] [--seed SEED]
```

### Parameters:
- `input`: Classical program file path or inline AML code string.
- `--backend`: Target backend identifier (default: `LOCAL_REFERENCE`).
- `--shots`: Shot sampling count for simulation (default: `1000`).
- `--seed`: Deterministic random seed for sampling (default: `None`).

---

## Execution Example

```bash
python -m src.application.cli.main compile "x = 5; y = 10" --backend LOCAL_REFERENCE --shots 1000 --seed 42
```

### Result:
Produces an end-to-end compiled logical circuit reference `LOG_CIRC_DEFAULT` and stores the materialized run record in `Output/Run_<timestamp>_<run_id>/`.
