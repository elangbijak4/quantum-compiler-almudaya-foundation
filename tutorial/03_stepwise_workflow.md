# 03. Stepwise Transformation Mode

Stepwise Mode empowers researchers to explicitly control each transformation stage without automatic chain expansion.

---

## The Stepwise Invariant

> **Rule**: Every transformation stage must be explicitly invoked. Running `aml` stops at AML and does NOT automatically trigger `utm`, `rutm`, `semantic`, `map`, `optimize`, `lower`, `simulate`, or `verify`.

---

## Step-by-Step Walkthrough

### Step 1: Classical Source -> Abstract Machine Language (AML)
```bash
python -m src.application.cli.main aml "x = 5"
```

### Step 2: AML -> Universal Turing Machine IR (UTM)
```bash
python -m src.application.cli.main utm AML_ART_01
```

### Step 3: UTM -> Reversible UTM IR (RUTM)
```bash
python -m src.application.cli.main rutm UTM_ART_01
```

### Step 4: RUTM -> Semantic Certificate
```bash
python -m src.application.cli.main semantic RUTM_ART_01
```

### Step 5: Semantic Certificate -> Logical Circuit Mapping
```bash
python -m src.application.cli.main map CERT_ART_01
```

### Step 6: Logical Circuit Optimization
```bash
python -m src.application.cli.main optimize LOG_CIRC_01
```

### Step 7: Native Circuit Lowering
```bash
python -m src.application.cli.main lower OPT_CIRC_01 --backend LOCAL_REFERENCE
```

### Step 8: Local Reference Simulation
```bash
python -m src.application.cli.main simulate NAT_CIRC_01 --shots 1000 --seed 42
```

### Step 9: Statistical Verification
```bash
python -m src.application.cli.main verify SIM_RES_01 --policy POLICY_DEFAULT
```
