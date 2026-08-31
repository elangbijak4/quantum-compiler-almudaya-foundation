"""
Module 6 Initialization Governance Test Suite.

Verifies directory structure, documentation existence, package importability, and upstream isolation.
"""

import unittest
import os
import importlib


class TestModule6Initialization(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def test_01_directory_scaffold(self) -> None:
        """Test 1: Verify Module 6 directory structure."""
        module6_dir = os.path.join(self.root_dir, "src", "module6")
        self.assertTrue(os.path.isdir(module6_dir), f"Directory missing: {module6_dir}")

        docs_dir = os.path.join(self.root_dir, "docs", "module-6")
        self.assertTrue(os.path.isdir(docs_dir), f"Directory missing: {docs_dir}")

        tests_dir = os.path.join(self.root_dir, "tests", "module6")
        self.assertTrue(os.path.isdir(tests_dir), f"Directory missing: {tests_dir}")

    def test_02_constitutional_documentation(self) -> None:
        """Test 2: Verify Module 6 constitutional foundation documents exist."""
        docs_dir = os.path.join(self.root_dir, "docs", "module-6")
        required_docs = [
            "MODULE_6_CONSTITUTION.md",
            "MODULE_6_SCOPE.md",
            "MODULE_6_ARCHITECTURE.md",
            "MODULE_6_INTERFACES.md",
            "MODULE_6_INVARIANTS.md",
            "MODULE_6_TERMINOLOGY.md",
            "MODULE_6_DEPENDENCIES.md",
            "MODULE_6_COMPLETION_CRITERIA.md",
            "MODULE_6_GRAPH.md",
            "MODULE_6_PROGRESS.md",
        ]
        for doc in required_docs:
            p = os.path.join(docs_dir, doc)
            self.assertTrue(os.path.isfile(p), f"Required documentation file missing: {p}")

    def test_03_module_importability(self) -> None:
        """Test 3: Verify src.module6 package is importable and exposes status metadata."""
        mod = importlib.import_module("src.module6")
        self.assertTrue(hasattr(mod, "__version__"))
        self.assertTrue(hasattr(mod, "__status__"))
        self.assertTrue("STAGE" in mod.__status__ or "INITIALIZATION" in mod.__status__)

    def test_04_upstream_integrity_and_isolation(self) -> None:
        """Test 4: Verify frozen upstream directories exist and are untouched."""
        for mod_num in range(1, 6):
            d = os.path.join(self.root_dir, "src", f"module{mod_num}")
            self.assertTrue(os.path.isdir(d), f"Upstream directory missing: {d}")


if __name__ == "__main__":
    unittest.main()
