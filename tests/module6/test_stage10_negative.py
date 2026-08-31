"""
Module 6 Stage 9 & 10 Test Suite — Negative Boundary & Immutability Verification Tests.
"""

import unittest
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    GateOperation,
    LogicalGateType,
    QubitRegister,
    RegisterType,
    QubitRef,
)
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.resolution import Stage7CompilerResolver
from src.module6.families.generators import AlgorithmFamilyGenerator
from src.module6.mapping.mapper import CompilerMapper
from src.module6.quality.model import QualityProfile, ResourceProfile, ResultClassification
from src.module6.analysis.stage10 import analyze_stage10_governance
from src.module6.governance import (
    CertificationLevel,
    LifecycleStatus,
)


class TestStage10Negative(unittest.TestCase):
    """Tests verifying negative semantic, unauthorized vocabulary, and input immutability cases in Stage 10."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_negative_semantic_verification_failure(self) -> None:
        """Semantic verification failure MUST cause certification to fail (AUDIT_FAILED / REJECTED)."""
        r_prof = ResourceProfile(
            total_qubits=2, data_qubits=2, ancilla_qubits=0,
            total_gate_count=1, circuit_depth=1, t_gate_count=0,
            t_gate_depth=0, cnot_gate_count=0, cnot_depth=0,
            gate_distribution={"X": 1},
        )
        fake_unverified_q_report = type("QualityAnalysisReportMock", (), {
            "quality_profile": QualityProfile(
                semantic_equivalence_verified=False, # Failed!
                feasibility_status="FEASIBLE",
                resource_profile=r_prof,
                optimization_reduction=0,
                vocabulary_compatibility=True,
                provenance_completeness=True,
                classification=ResultClassification.SEMANTICALLY_INVALID,
            ),
            "report_hash": "MOCK_UNVERIFIED_HASH",
            "classification": ResultClassification.SEMANTICALLY_INVALID,
        })()

        report = analyze_stage10_governance(self.circuit, self.ctx, quality_report=fake_unverified_q_report)

        self.assertEqual(report.certificate.certification_level, CertificationLevel.AUDIT_FAILED)
        self.assertEqual(report.certificate.lifecycle_status, LifecycleStatus.REJECTED)
        self.assertFalse(report.certificate.stage4_verified)
        self.assertIn("STAGE_4_SEMANTIC_VERIFICATION_FAILED", report.certificate.prerequisites_failed)

    def test_02_negative_unauthorized_vocabulary_case(self) -> None:
        """Circuit containing a gate outside G_effective MUST trigger vocabulary audit failure."""
        reg = QubitRegister(register_id="q", register_type=RegisterType.STATE, width=2)
        gate_unauth = GateOperation(gate_type="HADAMARD", target_qubit=QubitRef(register_id="q", index=0))
        unauth_circuit = QuantumCircuitIR(
            circuit_id="unauth_circ",
            registers=[reg],
            gates=[gate_unauth],
        )

        report = analyze_stage10_governance(unauth_circuit, self.ctx)

        self.assertFalse(report.certificate.stage7_feasible)
        self.assertIn("STAGE_7_VOCABULARY_OR_FEASIBILITY_FAILED", report.certificate.prerequisites_failed)
        self.assertNotEqual(report.certificate.certification_level, CertificationLevel.FULLY_GOVERNED_CERTIFIED)

    def test_03_input_immutability_verification(self) -> None:
        """Stage 10 audit MUST NOT mutate QuantumCircuitIR or EffectiveCompilationContext."""
        num_gates_before = len(self.circuit.gates)
        vocab_before = tuple(self.ctx.effective_vocabulary)

        analyze_stage10_governance(self.circuit, self.ctx)

        self.assertEqual(len(self.circuit.gates), num_gates_before)
        self.assertEqual(tuple(self.ctx.effective_vocabulary), vocab_before)


if __name__ == "__main__":
    unittest.main()
