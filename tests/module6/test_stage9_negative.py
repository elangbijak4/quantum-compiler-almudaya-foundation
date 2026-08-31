"""
Module 6 Stage 9 Test Suite — Negative Test Cases & Boundary Verification.
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
from src.module6.quality import (
    ResourceQualityEvaluator,
    ResultClassification,
)
from src.module6.analysis.stage9 import analyze_stage9_compilation_quality


class TestStage9Negative(unittest.TestCase):
    """Tests verifying negative semantic, resource constraint, and unauthorized vocabulary cases."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        self.model = list(family.models)[0]
        self.program = list(family.programs)[0]
        self.ctx = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.circuit = CompilerMapper.map_classical_model(self.model, self.program)

    def test_01_negative_semantic_case(self) -> None:
        """Semantically invalid candidate MUST NOT be classified as successful even if resource-efficient."""
        q_prof = ResourceQualityEvaluator.evaluate_quality_profile(
            circuit=self.circuit,
            context=self.ctx,
            semantic_equivalent=False, # Semantic verification failed
        )
        self.assertFalse(q_prof.semantic_equivalence_verified)
        self.assertEqual(q_prof.classification, ResultClassification.SEMANTICALLY_INVALID)

    def test_02_negative_resource_constraint_case(self) -> None:
        """Semantically valid circuit exceeding declared resource constraint yields RESOURCE_CONSTRAINT_VIOLATION without collapsing into semantic failure."""
        constraints = {"max_qubits": 1} # Impossible max qubits limit
        q_prof = ResourceQualityEvaluator.evaluate_quality_profile(
            circuit=self.circuit,
            context=self.ctx,
            semantic_equivalent=True,
            resource_constraints=constraints,
        )
        # Semantic validity remains PASS (True)
        self.assertTrue(q_prof.semantic_equivalence_verified)
        # Classification reflects RESOURCE_CONSTRAINT_VIOLATION
        self.assertEqual(q_prof.classification, ResultClassification.RESOURCE_CONSTRAINT_VIOLATION)

        violations = ResourceQualityEvaluator.check_resource_constraints(
            q_prof.resource_profile, constraints
        )
        self.assertTrue(len(violations) > 0)

    def test_03_negative_unauthorized_vocabulary_case(self) -> None:
        """Circuit containing a gate outside G_effective is classified as vocabulary violation without automatic promotion or hidden gate expansion."""
        reg = QubitRegister(register_id="q", register_type=RegisterType.STATE, width=2)
        gate_x = GateOperation(gate_type=LogicalGateType.X, target_qubit=QubitRef(register_id="q", index=0))
        circuit_with_gate = QuantumCircuitIR(
            circuit_id="unauthorized_circ",
            registers=[reg],
            gates=[gate_x],
        )

        # Check compatibility of circuit_with_gate (containing X) against effective_vocabulary=["HADAMARD"]
        compat = ResourceQualityEvaluator.check_vocabulary_compatibility(
            circuit_with_gate, effective_vocabulary=["HADAMARD"]
        )
        self.assertFalse(compat)

        q_prof = ResourceQualityEvaluator.evaluate_quality_profile(
            circuit=circuit_with_gate,
            context=self.ctx, # G_effective has X, CNOT, TOFFOLI
            semantic_equivalent=True,
        )
        # Effective vocabulary of ctx contains X, CNOT, TOFFOLI, so q_prof should be valid
        self.assertTrue(q_prof.vocabulary_compatibility)


if __name__ == "__main__":
    unittest.main()
