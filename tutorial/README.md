# Quantum Compiler CLI — User Tutorial & Documentation Package

Welcome to the official researcher-oriented user guide and tutorial for the **Quantum Compiler Production CLI** (`v1.0.0`).

The Quantum Compiler is a proof-oriented compiler pipeline that transforms classical algorithms into verified quantum circuits through a rigorous sequence of formal intermediate representations.

---

## 📚 Learning Path & Index

1. [**00. Quickstart Guide**](00_cli_quickstart.md): Get up and running in under 2 minutes with basic commands.
2. [**01. Command Reference**](01_command_reference.md): Detailed reference manual for all 13 production commands.
3. [**02. Pipeline Workflow Mode**](02_pipeline_workflow.md): Convenience one-shot compilation with `compile`.
4. [**03. Stepwise Transformation Mode**](03_stepwise_workflow.md): Step-by-step computational inspection (`aml` → `utm` → `rutm` → `semantic` → `map` → `optimize` → `lower`).
5. [**04. Artifact Chain & Identity**](04_artifact_chain.md): Understanding artifact IDs, hashes, parent/child linkage, and type safety.
6. [**05. Research Run & Output Archive**](05_research_run_and_output.md): Exploring persistent `Output/Run_<timestamp>_<run_id>/` archives, `manifest.json`, and run immutability.
7. [**06. Simulation & Shot Configuration**](06_simulation_and_shots.md): Local reference simulation, shot sampling (`--shots`), and seed reproducibility (`--seed`).
8. [**07. Statistical Verification**](07_verification.md): Verification metrics (Hellinger/KS distance) and status decisions (`VERIFIED`, `REJECTED`, `INCONCLUSIVE`).
9. [**08. Provenance & Lineage**](08_lineage_and_provenance.md): Read-only inspection (`inspect`, `lineage`) and Stage 11 historical lineage.
10. [**09. JSON & Automation**](09_json_and_automation.md): Machine-readable output (`--format json`) for scripting and laboratory integration.
11. [**10. Complete Researcher Workflow**](10_researcher_workflow.md): End-to-end research methodology guide from classical code to published paper evidence.
12. [**Example Playground**](examples/README.md): Interactive sample source files for hands-on practice.
13. [**Documentation Maintenance**](MAINTENANCE.md): Guidelines for keeping documentation synchronized with CLI updates.

---

## ⚡ Quick Prerequisites

- **Python**: Python 3.10+
- **Execution Entrypoint**: `python -m src.application.cli.main`
- **Global Flags**:
  - `--version`: Display version information.
  - `--help`: View interactive command list.
  - `--format {human,json}`: Choose output format.
