"""
Module 6 Stage 11 Test Suite — Negative Boundary & Immutability Verification Tests.
"""

import unittest
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.analysis.stage11 import analyze_stage11_lineage
from src.module6.lineage import (
    HistoricalLineageRepository,
    HistoricalLineageRecord,
)


class TestStage11Negative(unittest.TestCase):
    """Tests verifying negative boundary cases, hash tampering detection, and upstream immutability in Stage 11."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)
        self.repo = HistoricalLineageRepository()

    def test_01_tampered_record_hash_detection(self) -> None:
        """Repository verify_integrity MUST detect tampered record hashes and report violations."""
        tampered_rec = HistoricalLineageRecord(
            record_id="REC_TAMPERED",
            algorithm_id="ALG_TAMPERED",
            source_program_hash="SRC_HASH",
            audit_id="AUD_01",
            certificate_id="CERT_01",
            circuit_id="CIRC_01",
            vocabulary_hash="VOCAB_HASH",
            baseline_hash="BASE_HASH",
            optimization_id="OPT_01",
            quality_id="QUAL_01",
            semantic_evidence_id="SEM_01",
            governance_report_id="GOV_01",
            provenance_chain_hash="CHAIN_HASH",
            lifecycle_event_id="EVT_01",
            event_type="AUDIT_CERTIFIED",
            event_sequence=1,
            timestamp_identity="TS_01",
            record_hash="CORRUPTED_HASH_123", # Tampered!
        )
        self.repo.append_record(tampered_rec)

        integ = self.repo.verify_integrity()
        self.assertFalse(integ.is_integrity_valid)
        self.assertGreater(len(integ.violations), 0)
        self.assertIn("Record Hash Mismatch", integ.violations[0])

    def test_02_upstream_immutability_verification(self) -> None:
        """Stage 11 lineage tracing MUST NOT mutate QuantumCircuitIR or EffectiveCompilationContext."""
        num_gates_before = len(self.circuit.gates)
        vocab_before = tuple(self.ctx.effective_vocabulary)

        q_report = analyze_stage9_compilation_quality(self.circuit, self.ctx, model=self.model)
        audit_report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=q_report)
        analyze_stage11_lineage(audit_report, repository=self.repo)

        self.assertEqual(len(self.circuit.gates), num_gates_before)
        self.assertEqual(tuple(self.ctx.effective_vocabulary), vocab_before)


if __name__ == "__main__":
    unittest.main()
