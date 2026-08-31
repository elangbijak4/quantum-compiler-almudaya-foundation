# Quantum Compiler

A proof-oriented research prototype for a classical-to-quantum compiler
pipeline.

The project is developed incrementally, with every transformation treated
as an explicit compiler edge with defined boundaries, implementation,
verification, and certification.

---

## Attribution & Credits

This **Quantum Compiler** project was created by **Almudaya Quantum Labs**. 

We would like to extend our special credits and appreciation to:
- **Universitas Muhammadiyah Ponorogo**, Fakultas Teknik, Program Studi Teknik Informatika
- **Almudaya Research Institute Yogyakarta**

## License Status

🔒 Proprietary / All Rights Reserved

This project is currently in a pre-release development phase.

The source code is publicly visible for transparency,
research, architectural discussion, and evaluation.

No license is currently granted for copying, modification,
redistribution, commercial use, or creation of derivative works
without prior written permission.

The licensing model may change when the project reaches
a stable release.

## Tutorials

To understand how to use and navigate this project, please refer to our comprehensive tutorials:
- [00 CLI Quickstart](tutorial/00_cli_quickstart.md)
- [01 Command Reference](tutorial/01_command_reference.md)
- [02 Pipeline Workflow](tutorial/02_pipeline_workflow.md)
- [03 Stepwise Workflow](tutorial/03_stepwise_workflow.md)
- [04 Artifact Chain](tutorial/04_artifact_chain.md)
- [05 Research, Run, and Output](tutorial/05_research_run_and_output.md)
- [06 Simulation and Shots](tutorial/06_simulation_and_shots.md)
- [07 Verification](tutorial/07_verification.md)
- [08 Lineage and Provenance](tutorial/08_lineage_and_provenance.md)
- [09 JSON and Automation](tutorial/09_json_and_automation.md)
- [10 Researcher Workflow](tutorial/10_researcher_workflow.md)
- [Maintenance Guide](tutorial/MAINTENANCE.md)

---

## 1. Project Vision

The long-term compiler pipeline is:

```text
Classical Algorithm
        ↓
       AML
        ↓
      UTM
        ↓
 Reversible UTM
        ↓
    QTM / QUTM
        ↓
 Quantum Circuit
        ↓
Quantum Programming Language
        ↓
 Quantum Cloud Backend
```

The project does not implement the entire pipeline at once.

Each transformation is developed and verified independently.

The governing development principle is:

```text
PROVE
  ↓
IMPLEMENT
  ↓
VERIFY
  ↓
CERTIFY
  ↓
ADVANCE
```

---

## 2. Current Project Status

| Module | Transformation | Status |
|---|---|---|
| Module 1 | AML → UTM | **COMPLETE** |
| Module 2 | UTM → Reversible UTM | **COMPLETE** |
| Module 3 | Reversible UTM → QTM / QUTM | **COMPLETE** |
| Module 4 | QTM / QUTM → Quantum Circuit | **COMPLETE** |
| Module 5 | Extended Gate Vocabulary Synthesis | **COMPLETE** |
| Module 6 | Logical Mapping, Evolution & Governance | **COMPLETE** |
| Module 7 | Quantum Execution Engine & Backend | **COMPLETE** |

The current development status is therefore:

```text
Full End-State Compiler Pipeline (Modules 1 - 7 Complete)
```

The compiler has successfully advanced through all planned modules via iterative spiral development and is now fully capable of translating algorithmic code into optimized quantum circuits executing on cloud backends.


---

# 3. Module 1 — AML → UTM

Module 1 established the first certified compiler edge:

```text
AML
 ↓
AML-IR
 ↓
UTM-IR
 ↓
UTM Simulator
 ↓
Empirical Semantic Verification
 ↓
Certificate C1
```

Module 1 was completed through its completion gate and is now frozen.

Its primary output contract is:

```text
UTM-IR
Certificate C1
```

Module 2 consumes the UTM-IR produced by this frozen Module 1
pipeline.

### Module 1 scope

Module 1 defines a minimal Algorithmic Machine Language (AML), parses AML
into an intermediate representation, executes AML using a reference
interpreter, translates AML-IR into UTM-IR, executes the UTM representation,
and empirically verifies the observable results.

The initial AML instruction set is:

```text
LOAD
STORE
MOV

ADD
SUB
MUL
CMP

JMP
JZ
JNZ

HALT
```

The AML machine state is conceptually:

```text
S = (PC, R, M, F)
```

Module 1 also provides a UTM model, UTM simulator, dual execution,
semantic verification, and Certificate C1.

### Module 1 scientific boundary

Module 1 does **not** claim a universal theorem merely because finite
tests pass.

The distinction is:

```text
Mathematical proof
        ≠
Empirical verification
        ≠
Efficiency
```

The existing Module 1 verification is empirical and instance-based.

---

# 4. Module 2 — UTM → Reversible UTM

Module 2 extends the certified pipeline:

```text
UTM-IR
   ↓
Reversible UTM-IR
   ↓
Reversible UTM Simulator
   ↓
Forward / Reverse Verification
   ↓
Semantic Preservation Verification
   ↓
Certificate C2
```

## Core research question

Can a deterministic UTM computation be transformed into an extended
reversible computational model while preserving its observable semantics?

The initial target is:

```text
logical reversibility
computational reversibility
```

Thermodynamic reversibility is not claimed.

---

## 4.1 Reversibility boundary

Module 2 must distinguish:

### Logical reversibility

A computational transition is reversible/invertible under its formally
defined configuration model.

### Computational reversibility

The forward computation has an executable inverse that can recover the
preceding configuration(s).

### Thermodynamic reversibility

A physical claim involving entropy production, erasure, dissipation, or
thermodynamic implementation.

Module 2 does not establish thermodynamic reversibility unless a separate
physical analysis is explicitly performed.

In particular:

```text
Bijective computation
        ≠
Zero entropy production
```

The project must not make the stronger physical claim without the
appropriate physical model.

---

# 5. Module 2 Current Stage

Module 2 currently authorizes:

```text
Stage 1 — RUTM Specification
```

Stage 1 must establish the formal definition and boundary of the
Reversible UTM model before later implementation stages proceed.

Stage 1 should determine:

- RUTM definition;
- configuration tuple;
- forward transition;
- reverse transition;
- configuration equality;
- initial configuration;
- halting model;
- tape alphabet assumptions;
- auxiliary/history representation;
- domain and codomain;
- invariants;
- proof obligations;
- explicit non-claims.

A history or auxiliary register is a candidate construction, not an
assumption that reversibility has already been proved.

The relevant forward/inverse relationship must eventually have a formally
defined form such as:

```text
Forward:
    R(C, H) = (C', H')

Inverse:
    R⁻¹(C', H') = (C, H)
```

The exact construction is to be established by the Module 2 mathematical
specification.

### Stage 1 execution rule

The agent must:

1. read `main-technical-refference.md`;
2. read the frozen Module 1 documentation;
3. read `docs/module-2/MODULE_2_GRAPH.md`;
4. execute Stage 1 only;
5. document the result;
6. stop.

Later stages must not be implemented automatically.

---

# 6. Module 2 Scientific Boundaries

Module 2 was a classical reversible-computation module. Subsequent modules (3 through 7) have extended this to include:

- QTM/QUTM;
- quantum gates;
- quantum circuits;
- quantum cloud backends;
- IBM Quantum, Google Quantum, AWS Braket integrations.

---

# 7. Certificate Architecture

Each transformation in the long-term pipeline is intended to produce
its own evidence/certificate.

Current certified edge:

```text
C1:
AML → UTM
```

Target Module 2 certificate:

```text
C2:
UTM → Reversible UTM
```

Future certificates may correspond to:

```text
C3:
Reversible UTM → QTM / QUTM

C4:
QTM / QUTM → Quantum Circuit
```

Certificates are evidence artifacts. They must not be represented as
universal mathematical proofs unless a genuine formal proof establishes
the corresponding universal claim.

All certificates are stored in the unified:

```text
certificates/
```

directory.

---

# 8. Correctness and Efficiency

The project deliberately separates correctness from efficiency.

A transformation may be:

```text
semantically valid
```

while also being:

```text
inefficient
```

Efficiency evidence may include:

- execution steps;
- tape usage;
- auxiliary/history space;
- translation expansion;
- time overhead;
- space overhead.

Optimization is a separate concern and must not weaken correctness or
verification.

---

# 9. Repository Structure

The repository is a single unified project:

```text
quantum-compiler/
│
├── README.md
├── main-technical-refference.md
│
├── docs/
│   ├── architecture/
│   │   └── PIPELINE.md
│   │
│   ├── module-1/
│   │   ├── MODULE_1_GRAPH.md
│   │   └── ...
│   │
│   └── module-2/
│       ├── MODULE_2_GRAPH.md
│       └── ...
│
├── src/
│   ├── module1/
│   │   └── ...
│   │
│   └── module2/
│       └── ...
│
├── tests/
│   ├── module1/
│   │   └── ...
│   │
│   └── module2/
│       └── ...
│
├── examples/
│   ├── aml/
│   │   └── ...
│   │
│   └── utm/
│       └── ...
│
└── certificates/
    ├── README.md
    ├── C1_*.json
    └── C2_*.json
```

There must be exactly one authoritative root:

```text
README.md
main-technical-refference.md
```

There must be one authoritative:

```text
certificates/README.md
```

Module-specific documentation, source, and tests belong in their
respective module directories.

---

# 10. Development Methodology

Each module follows a controlled waterfall.

The general lifecycle is:

```text
Specification
      ↓
Formal Semantics
      ↓
Mathematical Proof / Proof Obligations
      ↓
Implementation
      ↓
Testing
      ↓
Verification
      ↓
Certificate
      ↓
Completion Gate
      ↓
Next Module
```

A later stage must not silently replace a missing proof obligation with
an implementation test.

A finite test suite does not automatically establish a universal theorem.

---

# 11. Module Isolation

Module 1 is frozen.

Module 2 may consume Module 1 outputs but must not silently modify Module 1.

If Module 2 discovers that the frozen UTM-IR contract is insufficient:

```text
STOP
  ↓
REPORT COMPATIBILITY ISSUE
  ↓
DO NOT SILENTLY MODIFY MODULE 1
```

Any revision to Module 1 must be an explicit project decision.

This preserves the validity and traceability of Certificate C1.

---

# 12. Current Development Entry Point

The current authorized entry point is:

```text
Module 2
    ↓
Stage 1
    ↓
RUTM Specification
```

The primary governing document is:

```text
main-technical-refference.md
```

The Module 1 frozen reference is:

```text
docs/module-1/MODULE_1_GRAPH.md
```

The Module 2 waterfall is:

```text
docs/module-2/MODULE_2_GRAPH.md
```

No later Module 2 stage should be implemented automatically.

---

# 13. Future Pipeline

After Module 2 has completed its own specification, proof,
implementation, verification, certification, and completion gate, future
modules may address:

```text
Reversible UTM
      ↓
QTM / QUTM
      ↓
Quantum Circuit
      ↓
Quantum Programming Language
      ↓
Cloud Quantum Backend
```

These future transformations require their own mathematical definitions,
proof obligations, verification procedures, and certificates.

They are not part of the current executable scope.

---

# 14. Final Project Principle

The objective is not merely to convert source code into quantum gates.

The objective is to construct a compiler in which each transformation is
independently:

```text
defined
formalized
proved where claimed
implemented
verified
certified
and analyzed for efficiency
```

The project therefore grows one certified transformation at a time.

Current state:

```text
C1:
AML → UTM
        │
        ▼
   COMPLETE / FROZEN

C2:
UTM → Reversible UTM
        │
        ▼
   ACTIVE / STAGE 1
```

The next transformation is not authorized until its mathematical and
engineering boundary has been established.

See `main-technical-refference.md` for the governing project rules.
