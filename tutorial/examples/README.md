# Tutorial Examples Playground

Interactive classical sample programs for learning and testing the Quantum Compiler CLI.

---

## Sample Files Index

| Filename | Purpose | Concept Demonstrated | Command to Run | Expected Status |
| :--- | :--- | :--- | :--- | :---: |
| `01_assignment.aml` | Simple assignment | Classical state allocation (`x = 5`) | `python -m src.application.cli.main compile tutorial/examples/01_assignment.aml` | SUCCESS |
| `02_multi_statement.aml` | Multiple assignments | Multi-variable environment (`x = 5; y = 10`) | `python -m src.application.cli.main compile tutorial/examples/02_multi_statement.aml` | SUCCESS |
| `03_expression.aml` | Expression evaluation | Binary addition (`x = 5; y = x + 10`) | `python -m src.application.cli.main compile tutorial/examples/03_expression.aml` | SUCCESS |
| `04_boolean_logic.aml` | Boolean logic | Bitwise AND (`a = 1; b = 0; c = a & b`) | `python -m src.application.cli.main compile tutorial/examples/04_boolean_logic.aml` | SUCCESS |
| `05_arithmetic.aml` | Arithmetic multiplication | Multiplication (`x = 10; y = 20; z = x * y`) | `python -m src.application.cli.main compile tutorial/examples/05_arithmetic.aml` | SUCCESS |
