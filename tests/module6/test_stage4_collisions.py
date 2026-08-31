"""
Module 6 Stage 4 Unit Test Suite — Collision Matrix & Semantic Collision Classification.

Verifies 3x3 collision matrix construction and collision classification (Types A, B, C, D).
"""

import unittest
from src.module6 import (
    AlgorithmFamilyGenerator,
    CompilerMapper,
    CollisionAnalyzer,
    CollisionType,
)


class TestStage4Collisions(unittest.TestCase):
    def setUp(self) -> None:
        fam1 = AlgorithmFamilyGenerator.generate_family("identity_family", size=1)
        fam2 = AlgorithmFamilyGenerator.generate_family("bit_flip_family", size=1)

        self.m1, self.p1 = fam1.models[0], fam1.programs[0]
        self.m2, self.p2 = fam2.models[0], fam2.programs[0]

        self.c1 = CompilerMapper.map_classical_model(self.m1, self.p1)
        self.c2 = CompilerMapper.map_classical_model(self.m2, self.p2)

    def test_01_syntactic_identity_collision(self) -> None:
        """Positive test: Pairwise collision analysis on identical model."""
        rec = CollisionAnalyzer.analyze_pair_collision(self.m1, self.m1, self.c1, self.c1)
        self.assertEqual(rec.collision_type, CollisionType.SYNTACTIC_IDENTITY)
        self.assertTrue(rec.classical_syntactic_equal)

    def test_02_type_d_distinct_mapping_collision(self) -> None:
        """Positive test: Classically different algorithms map to Type D distinct mapping."""
        rec = CollisionAnalyzer.analyze_pair_collision(self.m1, self.m2, self.c1, self.c2)
        self.assertEqual(rec.collision_type, CollisionType.TYPE_D_DISTINCT_MAPPING)
        self.assertFalse(rec.classical_semantic_equal)
        self.assertFalse(rec.quantum_semantic_equal)

    def test_03_3x3_collision_matrix_computation(self) -> None:
        """Positive test: 3x3 Collision Matrix computation."""
        rec1 = CollisionAnalyzer.analyze_pair_collision(self.m1, self.m1, self.c1, self.c1)
        rec2 = CollisionAnalyzer.analyze_pair_collision(self.m1, self.m2, self.c1, self.c2)

        mat = CollisionAnalyzer.compute_collision_matrix([rec1, rec2])
        self.assertIn("A1_eq_A2", mat)
        self.assertIn("A1_neq_A2", mat)
        self.assertEqual(mat["A1_eq_A2"]["F1_eq_F2"], 1)
        self.assertEqual(mat["A1_neq_A2"]["F1_neq_F2"], 1)


if __name__ == "__main__":
    unittest.main()
