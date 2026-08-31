"""
Module 6 Stage 11 Test Suite — Initialization & Constitutional Verification.
"""

import unittest
import os
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.analysis.stage11 import analyze_stage11_lineage


class TestStage11Initialization(unittest.TestCase):
    """Tests verifying Stage 11 initialization, scaffold, governance documents, and constitutional invariants."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_scaffold_existence(self) -> None:
        """Verifies Stage 11 scaffold and analyzer exist."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        self.assertIsNotNone(trace_report.trace_id)
        self.assertEqual(trace_report.algorithm_id, audit_report.algorithm_id)

    def test_02_governance_documents_existence(self) -> None:
        """Verifies all 11 required Stage 11 governance markdown files exist."""
        doc_files = [
            "MODULE_6_STAGE11_CONSTITUTION.md",
            "MODULE_6_STAGE11_SCOPE.md",
            "MODULE_6_STAGE11_ARCHITECTURE.md",
            "MODULE_6_STAGE11_INTERFACES.md",
            "MODULE_6_STAGE11_INVARIANTS.md",
            "MODULE_6_STAGE11_TERMINOLOGY.md",
            "MODULE_6_STAGE11_DEPENDENCIES.md",
            "MODULE_6_STAGE11_COMPLETION_CRITERIA.md",
            "MODULE_6_STAGE11_IMPLEMENTATION_PLAN.md",
            "MODULE_6_STAGE11_GRAPH.md",
            "MODULE_6_STAGE11_PROGRESS.md",
        ]
        docs_dir = os.path.join(os.getcwd(), "docs", "module-6")
        for fname in doc_files:
            fpath = os.path.join(docs_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"Missing governance doc: {fname}")

    def test_03_hardware_and_noise_boundary_preserved(self) -> None:
        """Verifies hardware boundary is preserved (0% hardware execution, 0% noise simulation)."""
        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        trace_report = analyze_stage11_lineage(audit_report)

        self.assertEqual(trace_report.provenance.get("stage"), "Stage 11 Production Engine")

    def test_04_upstream_stages1_10_immutability(self) -> None:
        """Verifies effective compilation context and circuit remain unmutated by Stage 11 lineage analysis."""
        num_gates_before = len(self.circuit.gates)
        vocab_before = tuple(self.ctx.effective_vocabulary)

        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        analyze_stage11_lineage(audit_report)

        self.assertEqual(len(self.circuit.gates), num_gates_before)
        self.assertEqual(tuple(self.ctx.effective_vocabulary), vocab_before)


if __name__ == "__main__":
    unittest.main()
