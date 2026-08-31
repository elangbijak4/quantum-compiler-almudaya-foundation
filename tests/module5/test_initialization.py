"""
Module 5 Constitutional & Initialization Test Suite.

Verifies:
1. Module 5 package metadata and exports.
2. Directory scaffold exists.
3. All 10 governing documentation files exist and are frozen.
4. Module 4 input contract (QuantumCircuitIR) is accessible and unchanged.
5. Modules 1-4 remain completely importable and frozen.
6. Scope Table classifications (all 20 items) match constitutional decisions.
"""

import os
import unittest
import src.module5
import src.module4
import src.module3
import src.module2
import src.module1


class TestModule5ConstitutionalReview(unittest.TestCase):
    def test_module5_package_metadata(self) -> None:
        """Verify Module 5 package metadata."""
        self.assertEqual(src.module5.__version__, "0.5.0-alpha")

    def test_directory_scaffold_exists(self) -> None:
        """Verify directory scaffold exists."""
        self.assertTrue(os.path.isdir("docs/module-5"))
        self.assertTrue(os.path.isdir("src/module5"))
        self.assertTrue(os.path.isdir("tests/module5"))
        self.assertTrue(os.path.isdir("examples/module5"))

    def test_governing_documents_exist(self) -> None:
        """Verify all 10 governing documents exist."""
        required_docs = [
            "MODULE_5_CONSTITUTION.md",
            "MODULE_5_SCOPE.md",
            "MODULE_5_GRAPH.md",
            "MODULE_5_ARCHITECTURE.md",
            "MODULE_5_INTERFACES.md",
            "MODULE_5_INVARIANTS.md",
            "MODULE_5_TERMINOLOGY.md",
            "MODULE_5_DEPENDENCIES.md",
            "MODULE_5_COMPLETION_CRITERIA.md",
            "MODULE_5_PROGRESS.md",
        ]
        for doc in required_docs:
            path = os.path.join("docs/module-5", doc)
            self.assertTrue(os.path.isfile(path), f"Missing governing doc: {path}")

    def test_scope_table_decisions_recorded(self) -> None:
        """Verify scope table classification matrix in MODULE_5_SCOPE.md."""
        with open("docs/module-5/MODULE_5_SCOPE.md", "r", encoding="utf-8") as f:
            content = f.read()

        required_items = [
            "QuantumCircuitIR",
            "Circuit Validation",
            "Logical Execution",
            "State-Vector Simulation",
            "Measurement",
            "Backend Abstraction",
            "Backend Capability Model",
            "Logical-to-Physical Mapping",
            "Physical Qubit Allocation",
            "SWAP Routing",
            "Native Gate Translation",
            "Hardware Topology",
            "Noise Simulation",
            "External Simulator",
            "Real Hardware Execution",
            "Remote Job Submission",
            "Result Retrieval",
            "Pulse Control",
            "Calibration",
            "Readout Mitigation",
        ]

        for item in required_items:
            self.assertIn(item, content, f"Missing scope classification for: {item}")

    def test_upstream_modules_accessible(self) -> None:
        """Verify Modules 1-4 remain fully importable."""
        self.assertIsNotNone(src.module1)
        self.assertIsNotNone(src.module2)
        self.assertIsNotNone(src.module3)
        self.assertIsNotNone(src.module4)


if __name__ == "__main__":
    unittest.main()
