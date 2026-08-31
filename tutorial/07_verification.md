# 07. Statistical Verification

Learn how Module 7 Stage 5 statistical verification evaluates simulation and execution results.

---

## Running Verification

```bash
python -m src.application.cli.main verify SIM_RES_01 --policy POLICY_DEFAULT
```

---

## Verification Status Decisions

Verification produces one of three distinct decisions:
1. `VERIFIED`: Observed probability distribution matches reference distribution within statistical threshold.
2. `REJECTED`: Observed distribution significantly deviates from expected distribution beyond threshold.
3. `INCONCLUSIVE`: Sample size (shots) is insufficient to render a statistically confident decision.

> **Crucial Distinction**: `INCONCLUSIVE` is NOT `REJECTED`. Statistical rejection is NOT semantic non-equivalence.
