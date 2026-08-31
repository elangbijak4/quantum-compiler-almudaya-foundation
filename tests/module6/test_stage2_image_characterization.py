"""
Module 6 Stage 2 Unit Test Suite — Image Characterization & Collision Analysis.

Tests algorithm family generation, image signature computation, empirical image construction Img_N(F) & OpImg_N(F),
structural vs operator identity separation, and collision detection.
"""

import unittest
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module4 import FiniteDomainContract
from src.module6 import (
    AlgorithmFamilyGenerator,
    EmpiricalImageCharacterizer,
    build_classical_semantic_model,
    CompilerMapper,
    CollisionType,
)


class TestStage2ImageCharacterization(unittest.TestCase):
    def setUp(self) -> None:
        self.prog = UTMProgram(
            states={"q0", "q_halt"},
            alphabet={"0", "1", "_"},
            blank_symbol="_",
            initial_state="q0",
            halt_state="q_halt",
            transitions={
                ("q0", "0"): TransitionAction("q_halt", "1", Direction.RIGHT),
            },
        )

    def test_01_algorithm_family_generation(self) -> None:
        """Positive test: AlgorithmFamilyGenerator builds valid family A_N subset A_C."""
        family = AlgorithmFamilyGenerator.generate_family("bit_flip_family", size=3)
        self.assertEqual(family.family_id, "bit_flip_family")
        self.assertEqual(len(family.models), 3)
        self.assertEqual(len(family.programs), 3)
        self.assertTrue(len(family.semantic_signature) > 0)

    def test_02_empirical_image_characterization(self) -> None:
        """Positive test: EmpiricalImageCharacterizer constructs Img_N(F) and OpImg_N(F)."""
        family = AlgorithmFamilyGenerator.generate_family("identity_family", size=3)
        circuits = [CompilerMapper.map_classical_model(m, p) for m, p in zip(family.models, family.programs)]

        summary = EmpiricalImageCharacterizer.characterize_image(family.models, circuits)
        self.assertEqual(summary.source_algorithm_count, 3)
        self.assertGreaterEqual(summary.circuit_image_count, 1)
        self.assertGreaterEqual(summary.operator_image_count, 1)
        self.assertEqual(len(summary.signatures), 3)

    def test_03_syntactic_circuit_collision_detection(self) -> None:
        """Positive test: CollisionAnalyzer detects collision when distinct algorithms map to identical circuits."""
        c0 = RUTMConfiguration(current_state="q_halt", tape={0: "1"}, head_pos=0, step_count=0, halted=True)
        contract = FiniteDomainContract(domain=[c0], execution_horizon=1, initial_configuration=c0)
        state_map = {"q0": 0, "q_halt": 1}
        symbol_map = {"_": 0, "0": 1, "1": 2}

        m1 = build_classical_semantic_model(self.prog, contract, state_map, symbol_map, "alg_1")
        m2 = build_classical_semantic_model(self.prog, contract, state_map, symbol_map, "alg_2")

        c1 = CompilerMapper.map_classical_model(m1, self.prog)
        c2 = CompilerMapper.map_classical_model(m2, self.prog)

        summary = EmpiricalImageCharacterizer.characterize_image([m1, m2], [c1, c2])
        self.assertTrue(len(summary.collisions) > 0)


if __name__ == "__main__":
    unittest.main()
