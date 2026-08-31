"""
Module 6 Stage 8 Test Suite — Effective Vocabulary Containment & Hadamard Invariant.
"""

import unittest
from src.module4.circuit_ir.model import (
    QuantumCircuitIR,
    QubitRegister,
    RegisterType,
    QubitRef,
    GateOperation,
    LogicalGateType,
)
from src.module6.evolution.state import create_initial_evolutionary_state
from src.module6.evolution.promotion import PromotionRecord, PromotionAuthorizationStatus
from src.module6.evolution.lineage import EvolutionaryLineageManager
from src.module6.resolution.resolver import Stage7CompilerResolver
from src.module6.optimization.optimizer import Stage8CircuitOptimizer
from src.module6.session.baseline import SessionBaseline, BaselineMode


class TestStage8Vocabulary(unittest.TestCase):
    """Tests enforcing absolute vocabulary containment and no hidden gate expansion invariant."""

    def setUp(self) -> None:
        self.ge0 = create_initial_evolutionary_state()
        self.mgr = EvolutionaryLineageManager(self.ge0)
        p_record = PromotionRecord(
            promotion_id="p_1",
            parent_evolution_stage=self.ge0.evolution_stage_id,
            candidate_gate_ids=("HADAMARD", "PHASE_S", "T_GATE"),
            candidate_hashes=("h1", "h2", "h3"),
            evidence_reference="EVID_STAGE5",
            equivalence_reference="EQUIV_STAGE5",
            authorization_status=PromotionAuthorizationStatus.EXPLICITLY_AUTHORIZED,
            authorized_by="ARCHITECT",
            promotion_timestamp="2026-08-24T00:00:00Z",
            resulting_vocabulary_hash="",
        )
        self.ge1 = self.mgr.promote_candidates(p_record, ("HADAMARD", "PHASE_S", "T_GATE"))
        self.ctx_ge0 = Stage7CompilerResolver.resolve_effective_context(self.ge0)
        self.ctx_ge1 = Stage7CompilerResolver.resolve_effective_context(self.ge1)

    def test_hadamard_cancellation_permitted_when_h_in_effective_vocabulary(self) -> None:
        """Req 26, 27: Hadamard cancellation is permitted ONLY when H exists in G_effective."""
        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=1)
        q0 = QubitRef("r0", 0)

        h_type = getattr(LogicalGateType, 'HADAMARD', 'HADAMARD')
        gates = [
            GateOperation(gate_type=h_type, target_qubit=q0, operation_index=0),
            GateOperation(gate_type=h_type, target_qubit=q0, operation_index=1),
        ]
        circuit_h = QuantumCircuitIR(circuit_id="c_h", registers=[reg], gates=gates)

        opt_h, report_h = Stage8CircuitOptimizer.optimize_circuit(circuit_h, self.ctx_ge1)
        self.assertTrue(report_h.vocabulary_containment_verified)
        self.assertEqual(report_h.optimized_metrics.total_gate_count, 0)

    def test_no_hidden_gate_expansion(self) -> None:
        """Req 20, 26: Optimizer does NOT introduce H or any gate outside G_effective."""
        reg = QubitRegister(register_id="r0", register_type=RegisterType.STATE, width=1)
        q0 = QubitRef("r0", 0)
        gates = [
            GateOperation(gate_type=LogicalGateType.X, target_qubit=q0, operation_index=0),
        ]
        circuit_x = QuantumCircuitIR(circuit_id="c_x", registers=[reg], gates=gates)

        opt_x, report_x = Stage8CircuitOptimizer.optimize_circuit(circuit_x, self.ctx_ge0)
        for g in opt_x.gates:
            g_name = g.gate_type.name if hasattr(g.gate_type, 'name') else str(g.gate_type)
            self.assertIn(g_name, self.ctx_ge0.effective_vocabulary)


if __name__ == "__main__":
    unittest.main()
