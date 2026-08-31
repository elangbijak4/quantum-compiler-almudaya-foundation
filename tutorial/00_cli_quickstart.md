# 00. CLI Quickstart Guide

Get started with the Quantum Compiler Production CLI in 2 minutes.

---

## 1. Verify Installation & Version

Run the `--version` command:

```bash
python -m src.application.cli.main --version
```

**Expected Output:**
```text
quantum-compiler v1.0.0
```

---

## 2. Discover Available Commands

Run the top-level `--help` command:

```bash
python -m src.application.cli.main --help
```

**Expected Output:**
```text
usage: quantum-compiler [-h] [--version] [--format {human,json}] [--config CONFIG]
                        {compile,aml,utm,rutm,semantic,map,optimize,lower,simulate,execute,verify,inspect,lineage} ...

Quantum Compiler Production CLI — Proof-Oriented Quantum Compiler Pipeline.
...
```

---

## 3. Run Your First Compilation (Pipeline Mode)

Compile a simple classical assignment program:

```bash
python -m src.application.cli.main compile "x = 5" --backend LOCAL_REFERENCE --shots 1000
```

**Expected Output:**
```text
=== Quantum Compiler CLI [COMPILE] ===
Operation    : compile
Status       : SUCCESS
Exit Code    : 0 (SUCCESS)
Request ID   : REQ_COMPILE_...
Response Hash: ...

--- Artifact References ---
  logical_circuit_id: LOG_CIRC_DEFAULT
  backend_id: LOCAL_REFERENCE

--- Evidence & Result Payload ---
  compiled: True
```

---

## 4. Run Local Reference Simulation

Simulate the resulting circuit with 1,000 shots and a deterministic seed:

```bash
python -m src.application.cli.main simulate LOG_CIRC_DEFAULT --shots 1000 --seed 42
```

**Expected Output:**
```text
=== Quantum Compiler CLI [SIMULATE] ===
Operation    : simulate
Status       : SUCCESS
Exit Code    : 0 (SUCCESS)

--- Evidence & Result Payload ---
  shots: 1000
  measurement_counts: {'00': 500, '11': 500}
```

---

## Next Steps

- Explore the [Command Reference](01_command_reference.md) for full syntax of all 13 commands.
- Try hands-on sample files in the [Example Playground](examples/README.md).
