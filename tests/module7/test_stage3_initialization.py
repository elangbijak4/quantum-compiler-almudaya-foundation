"""
Module 7 Stage 3 Test Suite — Initialization & Reference Simulator Data Contract Verification.
"""

import unittest
from src.module7.stage3 import (
    SimulationExecutionStatus,
    SimulatorConfig,
    ReferenceStatevectorSummary,
    SimulatorJobResult,
)


class TestModule7Stage3Initialization(unittest.TestCase):
    """Tests verifying Stage 3 foundational type contracts, config hashing, and immutability."""

    def test_01_simulator_config_hashing(self) -> None:
        """Verifies SimulatorConfig SHA-256 config_hash computation determinism."""
        c1 = SimulatorConfig(config_id="CFG_DEFAULT")
        c2 = SimulatorConfig(config_id="CFG_DEFAULT")
        self.assertEqual(len(c1.config_hash), 64)
        self.assertEqual(c1.config_hash, c2.config_hash)

    def test_02_reference_statevector_summary_hashing(self) -> None:
        """Verifies ReferenceStatevectorSummary canonical SHA-256 digest computation."""
        summary = ReferenceStatevectorSummary(
            qubit_count=2,
            probabilities={"00": 0.5, "11": 0.5},
        )
        self.assertEqual(len(summary.statevector_hash), 64)
        self.assertEqual(summary.probabilities["00"], 0.5)

    def test_03_simulator_job_result_integrity(self) -> None:
        """Verifies SimulatorJobResult fields and execution status representation."""
        job_res = SimulatorJobResult(
            job_id="JOB_SIM_01",
            native_circuit_id="NAT_CIRC_01",
            native_circuit_hash="a" * 64,
            backend_id="LOCAL_REF_SIM_01",
            capability_hash="b" * 64,
            lowering_id="LOWER_01",
            status=SimulationExecutionStatus.COMPLETED,
            shots=1000,
            measurement_counts={"00": 500, "11": 500},
            measurement_distribution={"00": 0.5, "11": 0.5},
        )
        self.assertEqual(job_res.status.value, "COMPLETED")
        self.assertEqual(len(job_res.job_hash), 64)


if __name__ == "__main__":
    unittest.main()
