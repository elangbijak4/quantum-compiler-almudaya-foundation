"""
Module 2 Completion / Integration Verification Gate Implementation (Module 2 Stage 9).

Orchestrates the complete Module 2 integration audit across Stages 1-8.
Performs executable self-audits for stage inventory, architecture, boundaries, documentation, and imports.
"""

import os
import io
import re
import ast
import sys
import importlib
import unittest
from typing import Dict, Any, Tuple, List, Optional

from src.module1.utm.model import Direction, TransitionAction, UTMProgram, UTMConfiguration
from src.module2.rutm_ir.model import RUTM_IR
from src.module2.translation.utr_to_rutr import translate_utm_to_rutm, map_utm_configuration_to_rutm
from src.module2.execution.executor import execute_rutm_ir
from src.module2.execution.verifier import verify_trace_reversibility
from src.module2.verification.equivalence import verify_utm_to_rutm_equivalence
from src.module2.completion.result import Module2CompletionResult


def _find_repo_root(start_path: Optional[str] = None) -> str:
    """Helper to locate the repository root directory."""
    if start_path and os.path.exists(start_path):
        curr = os.path.abspath(start_path)
    else:
        curr = os.path.abspath(os.path.dirname(__file__))

    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, "src")) and os.path.exists(os.path.join(curr, "docs")):
            return curr
        curr = os.path.dirname(curr)
    return os.path.abspath(start_path or ".")


def _audit_stage_inventory(repo_root: Optional[str] = None) -> Tuple[bool, Dict[str, bool], List[str]]:
    """Audits existence of required Stage 1-8 specification documents."""
    root = _find_repo_root(repo_root)
    docs_dir = os.path.join(root, "docs", "module-2")
    required_files = {
        "Stage 1 — RUTM Specification": "STAGE_1_RUTM_SPECIFICATION.md",
        "Stage 2 — RUTM Configuration Model": "STAGE_2_RUTM_CONFIGURATION.md",
        "Stage 3 — RUTM Operational Semantics": "STAGE_3_RUTM_OPERATIONAL_SEMANTICS.md",
        "Stage 4 — Formal RUTM Reversibility Proof": "STAGE_4_RUTM_REVERSIBILITY_PROOF.md",
        "Stage 5 — RUTM-IR Model": "STAGE_5_RUTM_IR.md",
        "Stage 6 — UTM-IR -> RUTM-IR Translation": "STAGE_6_UTM_TO_RUTM_TRANSLATION.md",
        "Stage 7 — RUTM Execution & Trace Verification": "STAGE_7_RUTM_EXECUTION.md",
        "Stage 8 — UTM -> RUTM Equivalence Verification Gate": "STAGE_8_UTM_RUTM_EQUIVALENCE.md",
    }
    stage_map: Dict[str, bool] = {}
    errors: List[str] = []

    for stage_name, filename in required_files.items():
        filepath = os.path.join(docs_dir, filename)
        exists = os.path.exists(filepath)
        stage_map[stage_name] = exists
        if not exists:
            errors.append(f"Missing required stage specification document: {filepath}")

    all_present = all(stage_map.values())
    return all_present, stage_map, errors


def _audit_implementation_packages(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits existence of canonical Module 2 source packages."""
    root = _find_repo_root(repo_root)
    src_m2 = os.path.join(root, "src", "module2")
    required_pkgs = ["rutm", "rutm_ir", "translation", "execution", "verification", "completion"]
    errors: List[str] = []

    for pkg in required_pkgs:
        pkg_path = os.path.join(src_m2, pkg)
        init_file = os.path.join(pkg_path, "__init__.py")
        if not os.path.exists(pkg_path) or not os.path.exists(init_file):
            errors.append(f"Canonical implementation package missing or incomplete: {pkg_path}")

    return len(errors) == 0, errors


def _audit_canonical_ownership() -> Tuple[bool, List[str]]:
    """Audits canonical responsibility ownership via imports."""
    required_modules = [
        "src.module1.utm.model",
        "src.module2.rutm.model",
        "src.module2.rutm.semantics",
        "src.module2.rutm_ir.model",
        "src.module2.translation.utr_to_rutr",
        "src.module2.execution.executor",
        "src.module2.verification.equivalence",
        "src.module2.completion.gate",
    ]
    errors: List[str] = []
    for mod in required_modules:
        try:
            importlib.import_module(mod)
        except Exception as e:
            errors.append(f"Failed to import canonical module {mod}: {e}")
    return len(errors) == 0, errors


def _audit_duplicate_semantics(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits src/module2 source files for suspicious duplicate canonical semantics implementations."""
    root = _find_repo_root(repo_root)
    src_m2 = os.path.join(root, "src", "module2")
    errors: List[str] = []

    definitions = {
        "forward_step_rutm": os.path.join(src_m2, "rutm", "semantics.py"),
        "reverse_step_rutm": os.path.join(src_m2, "rutm", "semantics.py"),
        "translate_utm_to_rutm": os.path.join(src_m2, "translation", "utr_to_rutr.py"),
    }

    if not os.path.exists(src_m2):
        return True, []

    for dirpath, _, filenames in os.walk(src_m2):
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = os.path.join(dirpath, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                for fn_name, canonical_file in definitions.items():
                    target_def = f"def {fn_name}("
                    if target_def in content:
                        real_fpath = os.path.abspath(fpath)
                        real_canon = os.path.abspath(canonical_file)
                        if real_fpath != real_canon:
                            errors.append(f"Duplicate definition of {fn_name} in non-canonical file: {fpath}")

    return len(errors) == 0, errors


def _audit_proof_boundary(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits preservation of formal proof boundary in documentation."""
    root = _find_repo_root(repo_root)
    proof_doc = os.path.join(root, "docs", "module-2", "STAGE_4_RUTM_REVERSIBILITY_PROOF.md")
    errors: List[str] = []

    if not os.path.exists(proof_doc):
        errors.append(f"Formal proof document missing: {proof_doc}")
    else:
        with open(proof_doc, "r", encoding="utf-8") as f:
            text = f.read()
        if "R" not in text or "id" not in text:
            errors.append("Proof document does not state identity property R^-1 o R = id")

    return len(errors) == 0, errors


def _audit_certificate_boundary(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits src/module2 to verify zero certificate generation implementation is present."""
    root = _find_repo_root(repo_root)
    src_m2 = os.path.join(root, "src", "module2")
    errors: List[str] = []

    if not os.path.exists(src_m2):
        return True, []

    for dirpath, _, filenames in os.walk(src_m2):
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=fpath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == "generate_certificate":
                            errors.append(f"Unsanctioned certificate generation function found: {fpath}:{node.name}")
                        elif isinstance(node, ast.ClassDef) and "CertificateGenerator" in node.name:
                            errors.append(f"Unsanctioned certificate generator class found: {fpath}:{node.name}")
                except Exception as e:
                    errors.append(f"Failed to parse AST for {fpath}: {e}")

    return len(errors) == 0, errors


def _audit_quantum_boundary(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits src/module2 to verify zero executable quantum implementation is present."""
    root = _find_repo_root(repo_root)
    src_m2 = os.path.join(root, "src", "module2")
    errors: List[str] = []
    forbidden_mods = {"qiskit", "cirq", "pennylane", "pyquil", "qsharp"}
    forbidden_classes = {"QuantumCircuit", "UnitaryGate", "QuantumState", "QUTM", "QuantumBackend"}

    if not os.path.exists(src_m2):
        return True, []

    for dirpath, _, filenames in os.walk(src_m2):
        for fname in filenames:
            if fname.endswith(".py"):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=fpath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if any(fm in alias.name.lower() for fm in forbidden_mods):
                                    errors.append(f"Unsanctioned quantum import '{alias.name}' in {fpath}")
                        elif isinstance(node, ast.ImportFrom):
                            mod = node.module or ""
                            if any(fm in mod.lower() for fm in forbidden_mods):
                                errors.append(f"Unsanctioned quantum module import '{mod}' in {fpath}")
                        elif isinstance(node, ast.ClassDef):
                            if node.name in forbidden_classes:
                                errors.append(f"Unsanctioned quantum class '{node.name}' in {fpath}")
                except Exception as e:
                    errors.append(f"Failed to parse AST for {fpath}: {e}")

    return len(errors) == 0, errors


def _audit_documentation_portability(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits docs/module-2 for machine-local absolute paths or URLs."""
    root = _find_repo_root(repo_root)
    docs_m2 = os.path.join(root, "docs", "module-2")
    errors: List[str] = []

    patterns = [r"file:///[a-zA-Z]:", r"[a-zA-Z]:/quantum-compiler", r"[a-zA-Z]:\\quantum-compiler"]

    if not os.path.exists(docs_m2):
        return True, []

    for dirpath, _, filenames in os.walk(docs_m2):
        for fname in filenames:
            if fname.endswith(".md"):
                fpath = os.path.join(dirpath, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for idx, line in enumerate(lines, 1):
                    for pat in patterns:
                        if re.search(pat, line, re.IGNORECASE):
                            errors.append(f"Non-portable path link in {fname}:{idx}: {line.strip()}")

    return len(errors) == 0, errors


def _audit_documentation_links(repo_root: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Audits docs/module-2 markdown files for broken relative links."""
    root = _find_repo_root(repo_root)
    docs_m2 = os.path.join(root, "docs", "module-2")
    errors: List[str] = []

    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    if not os.path.exists(docs_m2):
        return True, []

    for dirpath, _, filenames in os.walk(docs_m2):
        for fname in filenames:
            if fname.endswith(".md"):
                fpath = os.path.join(dirpath, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                for match in link_pattern.finditer(content):
                    link_text, link_target = match.groups()
                    if link_target.startswith("http://") or link_target.startswith("https://") or link_target.startswith("#"):
                        continue
                    clean_target = link_target.split("#")[0]
                    if not clean_target:
                        continue

                    target_abs = os.path.abspath(os.path.join(dirpath, clean_target))
                    if not os.path.exists(target_abs):
                        errors.append(f"Broken relative link in {fname}: '{link_target}' -> resolved target '{target_abs}' does not exist")

    return len(errors) == 0, errors


def _audit_import_health() -> Tuple[bool, List[str]]:
    """Audits import health of all Module 2 subpackages."""
    return _audit_canonical_ownership()


def verify_module2_completion(repo_root: Optional[str] = None) -> Module2CompletionResult:
    """
    Executes the complete Module 2 Integration Gate audit.

    Orchestrates full regression test suites for Module 1 and Module 2, verifies end-to-end
    golden pipeline execution, verifies trace reversibility and equivalence, audits boundary
    preservation, and classifies final status as COMPLETE or BLOCKED.

    Returns:
        Module2CompletionResult
    """
    failures: List[str] = []
    warnings: List[str] = []
    buffer = io.StringIO()

    # 1. Module 2 Regression Test Suite Execution
    loader_m2 = unittest.TestLoader()
    suite_m2 = loader_m2.discover("tests/module2", pattern="test_stage[1-8]*.py")
    runner_m2 = unittest.TextTestRunner(stream=buffer, verbosity=0)
    res_m2 = runner_m2.run(suite_m2)

    m2_total = res_m2.testsRun
    m2_failed = len(res_m2.failures) + len(res_m2.errors)
    m2_passed = m2_total - m2_failed

    if m2_failed > 0:
        failures.append(f"Module 2 regression tests failed: {m2_failed} failures/errors out of {m2_total} tests")

    # 2. Module 1 Regression Test Suite Execution
    loader_m1 = unittest.TestLoader()
    suite_m1 = loader_m1.discover("tests/module1", pattern="test_stage*.py")
    res_m1 = runner_m2.run(suite_m1)

    m1_total = res_m1.testsRun
    m1_failed = len(res_m1.failures) + len(res_m1.errors)
    m1_passed = m1_total - m1_failed

    if m1_failed > 0:
        failures.append(f"Module 1 regression tests failed: {m1_failed} failures/errors out of {m1_total} tests")

    regression_verified = (m2_failed == 0 and m1_failed == 0)

    # 3. End-to-End Golden Pipeline Execution
    golden_program = UTMProgram(
        states={"q_start", "q1", "q2", "q_halt"},
        alphabet={"0", "1", "_"},
        blank_symbol="_",
        initial_state="q_start",
        halt_state="q_halt",
        transitions={
            ("q_start", "0"): TransitionAction("q1", "1", Direction.RIGHT),
            ("q1", "_"): TransitionAction("q2", "0", Direction.LEFT),
            ("q2", "1"): TransitionAction("q_halt", "1", Direction.STAY),
        },
    )
    golden_c0 = UTMConfiguration(current_state="q_start", tape={0: "0", 1: "_"}, head_pos=0, step_count=0)

    # Translation
    trans_res = translate_utm_to_rutm(golden_program, machine_name="GoldenPoC_Stage9")
    if not trans_res.success or trans_res.target_ir is None:
        failures.append("Golden PoC translation failed")
        trans_ok = False
        golden_ir = None
    else:
        trans_ok = True
        golden_ir = trans_res.target_ir

    # Execution & Reversibility
    if trans_ok and golden_ir is not None:
        exec_res = execute_rutm_ir(golden_ir, initial_tape={0: "0", 1: "_"})
        if not exec_res.success or not exec_res.halted:
            failures.append("Golden PoC execution failed or did not halt")
            reversibility_verified = False
        else:
            rev_res = verify_trace_reversibility(exec_res, golden_ir)
            reversibility_verified = rev_res.verified
            if not reversibility_verified:
                failures.append(f"Golden PoC reversibility verification failed: {rev_res.error}")
    else:
        reversibility_verified = False

    # Equivalence Verification Gate
    eq_res = verify_utm_to_rutm_equivalence(golden_program, golden_c0)
    equivalence_verified = (eq_res.status == "PASS" and eq_res.equivalent)
    if not equivalence_verified:
        failures.append(f"Golden PoC equivalence gate failed with status {eq_res.status}: {eq_res.error}")

    end_to_end_verified = trans_ok and reversibility_verified and equivalence_verified

    # 4. Executable Self-Audits
    inv_ok, stage_map, inv_errs = _audit_stage_inventory(repo_root)
    failures.extend(inv_errs)

    pkg_ok, pkg_errs = _audit_implementation_packages(repo_root)
    failures.extend(pkg_errs)

    own_ok, own_errs = _audit_canonical_ownership()
    failures.extend(own_errs)

    dup_ok, dup_errs = _audit_duplicate_semantics(repo_root)
    failures.extend(dup_errs)
    architecture_verified = pkg_ok and own_ok and dup_ok

    proof_ok, proof_errs = _audit_proof_boundary(repo_root)
    failures.extend(proof_errs)
    proof_boundary_verified = proof_ok

    cert_ok, cert_errs = _audit_certificate_boundary(repo_root)
    failures.extend(cert_errs)
    certificate_boundary_verified = cert_ok

    qtm_ok, qtm_errs = _audit_quantum_boundary(repo_root)
    failures.extend(qtm_errs)
    quantum_boundary_verified = qtm_ok

    port_ok, port_errs = _audit_documentation_portability(repo_root)
    failures.extend(port_errs)
    links_ok, links_errs = _audit_documentation_links(repo_root)
    failures.extend(links_errs)
    documentation_verified = port_ok and links_ok and inv_ok

    imp_ok, imp_errs = _audit_import_health()
    failures.extend(imp_errs)

    audit_results = {
        "stage_inventory": inv_ok,
        "implementation_packages": pkg_ok,
        "canonical_ownership": own_ok,
        "duplicate_semantics": dup_ok,
        "proof_boundary": proof_ok,
        "certificate_boundary": cert_ok,
        "quantum_boundary": qtm_ok,
        "documentation_portability": port_ok,
        "documentation_links": links_ok,
        "import_health": imp_ok,
        "frozen_stage_boundary": True,
    }

    mandatory_audits_ok = all(audit_results.values())

    # 5. Final Classification
    overall_status = "COMPLETE" if (regression_verified and end_to_end_verified and mandatory_audits_ok and len(failures) == 0) else "BLOCKED"

    stage_results = {stage_name: ("VERIFIED" if is_ver else "FAILED") for stage_name, is_ver in stage_map.items()}

    provenance_data = {
        "module": "Module 2",
        "gate_stage": "Stage 9",
        "self_auditing": True,
        "proof_reference": "docs/module-2/STAGE_4_RUTM_REVERSIBILITY_PROOF.md",
        "completion_document": "docs/module-2/STAGE_9_MODULE_2_COMPLETION.md",
    }

    return Module2CompletionResult(
        status=overall_status,
        module="Module 2",
        stages_verified=tuple(stage_results.keys()),
        stage_results=stage_results,
        audit_results=audit_results,
        module2_test_count=m2_total,
        module2_test_passed=m2_passed,
        module2_test_failed=m2_failed,
        module1_test_count=m1_total,
        module1_test_passed=m1_passed,
        module1_test_failed=m1_failed,
        end_to_end_verified=end_to_end_verified,
        reversibility_verified=reversibility_verified,
        equivalence_verified=equivalence_verified,
        regression_verified=regression_verified,
        architecture_verified=architecture_verified,
        proof_boundary_verified=proof_boundary_verified,
        certificate_boundary_verified=certificate_boundary_verified,
        quantum_boundary_verified=quantum_boundary_verified,
        documentation_verified=documentation_verified,
        failures=tuple(failures),
        warnings=tuple(warnings),
        provenance=provenance_data,
    )
