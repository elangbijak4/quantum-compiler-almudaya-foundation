# 06. Local Simulation & Shot Configuration

Guide to running local reference simulations and controlling sampling parameters.

---

## Running Local Reference Simulation

```bash
python -m src.application.cli.main simulate LOG_CIRC_DEFAULT --shots 1000 --seed 42
```

### Key Flags:
- `--shots N`: Specifies sampling shot count (must be `N > 0`).
- `--seed N`: Sets deterministic random seed for reproducible sampling.

---

## Distinguishing Shot Model Fields

The CLI preserves distinct shot metadata fields:
- `requested_shots`: Shots requested by user (e.g. 1000).
- `submitted_shots`: Shots submitted to simulation engine (1000).
- `actual_returned_shots`: Total measurements collected (1000).

> **No Silent Shot Increase**: The CLI will never automatically alter or increase shot counts behind the user's back.
