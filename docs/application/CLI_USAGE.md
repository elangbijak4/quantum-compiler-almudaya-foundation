# APPLICATION / PRODUCT LAYER — CLI USAGE GUIDE

## Global Options
- `--version`: Display version information (`quantum-compiler v1.0.0`).
- `--format {human,json}`: Choose output format.
- `--config <path>`: Specify path to configuration file.

## Example Invocations

### 1. Convenience Pipeline Mode
```bash
python -m src.application.cli.main compile "x = 5" --backend LOCAL_REFERENCE --shots 1000
```

### 2. Stepwise Transformation Commands
```bash
python -m src.application.cli.main aml program.aml
python -m src.application.cli.main utm aml:01
python -m src.application.cli.main rutm utm:01
python -m src.application.cli.main semantic rutm:01
python -m src.application.cli.main map cert:01
python -m src.application.cli.main optimize circ:01
python -m src.application.cli.main lower circ:01 --backend LOCAL_REFERENCE
```

### 3. Execution Commands
```bash
python -m src.application.cli.main simulate nat:01 --shots 1000
python -m src.application.cli.main execute nat:01 --backend LOCAL_REFERENCE --shots 1000
```

### 4. Read-Only Inspection Commands
```bash
python -m src.application.cli.main inspect LOCAL_REFERENCE
python -m src.application.cli.main lineage LOG_CIRC_01
```
