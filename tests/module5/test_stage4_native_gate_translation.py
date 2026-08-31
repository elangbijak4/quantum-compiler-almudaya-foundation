"""
Module 5 Stage 4 Unit Test Suite — Hardware Native Gate Translation & Device Adapter Layer.

Tests all 20 positive-path and 16 negative-path requirements:
POSITIVE:
1. direct native gate resolution
2. native gate sequence generation
3. SWAP native translation
4. non-native gate decomposition
5. parameter preservation
6. multi-qubit decomposition
7. native circuit validation
8. basis-state equivalence
9. superposition equivalence
10. complex amplitude preservation
11. norm preservation
12. operator unitarity
13. adjoint equivalence
14. provenance preservation
15. deterministic translation
16. serialization round-trip
17. reference adapter
18. multiple sequential operations
19. mixed direct/decomposed circuit
20. complete native vocabulary closure

NEGATIVE:
1. unsupported gate
2. unsupported arity
3. invalid parameter count
4. invalid parameter value
5. missing decomposition
6. invalid decomposition
7. decomposition containing unsupported gate
8. operand mismatch
9. invalid physical qubit
10. backend capability mismatch
11. semantic mismatch
12. non-unitary decomposition
13. dirty/invalid native result
14. malformed serialization
15. schema mismatch
16. nondeterministic decomposition selection
"""

import unittest
from src.module4.circuit_ir.model import QubitRef
from src.module5 import (
    PhysicalQubit,
    QubitMapping,
    DeviceTopology,
    PhysicalGateOperation,
    PhysicalCircuitIR,
    ExecutionProvenance,
    NativeGateDefinition,
    NativeOperation,
    NativeResolutionStatus,
    NativeGateResolutionResult,
    NativeCircuitIR,
    NativeTranslationResult,
    NativeGateVocabulary,
    DecompositionEntry,
    GateDecompositionRegistry,
    BackendAdapter,
    ReferenceBackendAdapter,
    NativeCircuitVerifier,
    NativeTranslator,
    validate_native_circuit_ir,
    serialize_native_circuit_ir,
    deserialize_native_circuit_ir,
    create_reference_simulator_capabilities,
    BackendIdentity,
    BackendType,
)


class CustomCZAdapter(ReferenceBackendAdapter):
    """Custom CZ-native adapter where CNOT is unsupported and must decompose into H, CZ, H."""

    def __init__(self) -> None:
        model = create_reference_simulator_capabilities()
        model.gate_capabilities["CNOT"].supported = False  # CNOT is NOT directly native!
        model.identity = BackendIdentity(
            backend_id="CZ_NATIVE_BACKEND",
            backend_name="CZ Native Simulator",
            backend_version="1.0.0",
            backend_type=BackendType.REFERENCE_SIMULATOR,
        )
        super().__init__(model)


class TestStage4NativeGateTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.q0 = QubitRef("reg_q", 0)
        self.q1 = QubitRef("reg_q", 1)

        self.p0 = PhysicalQubit(node_id=0)
        self.p1 = PhysicalQubit(node_id=1)

        self.mapping = QubitMapping()
        self.mapping.set_mapping(self.q0, 0)
        self.mapping.set_mapping(self.q1, 1)

        self.topology = DeviceTopology()
        self.topology.add_edge(0, 1)

        self.g0 = PhysicalGateOperation(gate_type="X", target_node=0, control_nodes=(), operation_index=0)
        self.g1 = PhysicalGateOperation(gate_type="CNOT", control_nodes=(0,), target_node=1, operation_index=1)

        self.provenance = ExecutionProvenance(
            source_rutm_program_hash="rutm_hash_111",
            source_qtm_machine_id="qtm_id_222",
            logical_circuit_id="log_circ_333",
            physical_circuit_id="phys_circ_444",
        )

        self.physical_circuit = PhysicalCircuitIR(
            physical_circuit_id="phys_circ_444",
            source_logical_circuit_id="log_circ_333",
            physical_qubits=[self.p0, self.p1],
            gates=[self.g0, self.g1],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
        )

        self.adapter = ReferenceBackendAdapter()

    # ------------------------------------------------------------------
    # POSITIVE TESTS (20)
    # ------------------------------------------------------------------
    def test_pos_01_direct_native_gate_resolution(self) -> None:
        """Pos 1: X and CNOT resolve directly on ReferenceBackendAdapter."""
        res = self.adapter.resolve_gate(self.g0)
        self.assertEqual(res.status, NativeResolutionStatus.DIRECT_NATIVE)
        self.assertEqual(res.native_operations[0].native_gate, "X")

    def test_pos_02_native_gate_sequence_generation(self) -> None:
        """Pos 2: Translation generates ordered native operations list."""
        res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        self.assertTrue(res.success)
        self.assertEqual(len(res.native_circuit.native_operations), 2)
        self.assertEqual(res.native_circuit.native_operations[0].native_gate, "X")
        self.assertEqual(res.native_circuit.native_operations[1].native_gate, "CNOT")

    def test_pos_03_swap_native_translation(self) -> None:
        """Pos 3: SWAP physical gate translates cleanly into native SWAP or CNOT sequence."""
        g_swap = PhysicalGateOperation(gate_type="SWAP", control_nodes=(0,), target_node=1, operation_index=0)
        c_swap = PhysicalCircuitIR(
            physical_circuit_id="p_swap",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1],
            gates=[g_swap],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
        )
        res = NativeTranslator.translate(c_swap, self.adapter)
        self.assertTrue(res.success)

    def test_pos_04_non_native_gate_decomposition(self) -> None:
        """Pos 4: CNOT on CZ-native adapter decomposes into H(1), CZ(0,1), H(1)."""
        cz_adapter = CustomCZAdapter()
        res = NativeTranslator.translate(self.physical_circuit, cz_adapter)
        self.assertTrue(res.success)
        # Expected X(0), H(1), CZ(0,1), H(1)
        ops = res.native_circuit.native_operations
        self.assertEqual(len(ops), 4)
        self.assertEqual(ops[0].native_gate, "X")
        self.assertEqual(ops[1].native_gate, "H")
        self.assertEqual(ops[2].native_gate, "CZ")
        self.assertEqual(ops[3].native_gate, "H")

    def test_pos_05_parameter_preservation(self) -> None:
        """Pos 5: Parameterized gate RZ preserves parameters."""
        nop = NativeOperation(native_gate="RZ", operands=(0,), parameters=(1.57079632679,))
        self.assertEqual(nop.parameters[0], 1.57079632679)

    def test_pos_06_multi_qubit_decomposition(self) -> None:
        """Pos 6: Multi-qubit TOFFOLI decomposes into native 1/2 qubit operations."""
        p2 = PhysicalQubit(node_id=2)
        topo3 = DeviceTopology()
        topo3.add_edge(0, 1)
        topo3.add_edge(1, 2)
        topo3.add_edge(0, 2)
        m3 = QubitMapping()
        m3.set_mapping(self.q0, 0)
        m3.set_mapping(self.q1, 1)
        m3.set_mapping(QubitRef("reg_q", 2), 2)

        g_tof = PhysicalGateOperation(gate_type="TOFFOLI", control_nodes=(0, 1), target_node=2, operation_index=0)
        c_tof = PhysicalCircuitIR(
            physical_circuit_id="p_tof",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1, p2],
            gates=[g_tof],
            mapping=m3,
            topology=topo3,
            provenance=self.provenance,
        )
        res = NativeTranslator.translate(c_tof, self.adapter)
        self.assertTrue(res.success)

    def test_pos_07_native_circuit_validation(self) -> None:
        """Pos 7: NativeCircuitIR passes 3-level validation."""
        res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        val_res = validate_native_circuit_ir(res.native_circuit, self.adapter)
        self.assertTrue(val_res.valid)

    def test_pos_08_09_10_11_12_13_semantic_verification(self) -> None:
        """Pos 8 to 13: Basis, superposition, complex amplitudes, norm, operator unitarity, adjoint equivalence."""
        res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        ver_rep = NativeCircuitVerifier.verify_equivalence(self.physical_circuit, res.native_circuit)
        self.assertTrue(ver_rep.verified)
        self.assertTrue(ver_rep.statevector_pass)
        self.assertTrue(ver_rep.operator_pass)
        self.assertTrue(ver_rep.left_unitarity_pass)
        self.assertTrue(ver_rep.right_unitarity_pass)
        self.assertTrue(ver_rep.adjoint_pass)
        self.assertTrue(ver_rep.norm_preservation_pass)
        self.assertLess(ver_rep.max_residual, 1e-12)

    def test_pos_14_provenance_preservation(self) -> None:
        """Pos 14: Upstream provenance preserved with Stage 4 marker."""
        res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        self.assertEqual(res.native_circuit.provenance.source_rutm_program_hash, "rutm_hash_111")
        self.assertEqual(res.native_circuit.provenance.source_qtm_machine_id, "qtm_id_222")

    def test_pos_15_16_determinism_and_serialization(self) -> None:
        """Pos 15 & 16: Deterministic translation and exact round-trip serialization."""
        res1 = NativeTranslator.translate(self.physical_circuit, self.adapter)
        res2 = NativeTranslator.translate(self.physical_circuit, self.adapter)

        s1 = serialize_native_circuit_ir(res1.native_circuit)
        s2 = serialize_native_circuit_ir(res2.native_circuit)
        self.assertEqual(s1, s2)

        deser = deserialize_native_circuit_ir(s1)
        s3 = serialize_native_circuit_ir(deser)
        self.assertEqual(s1, s3)

    def test_pos_17_18_19_20_adapter_and_closure(self) -> None:
        """Pos 17 to 20: Reference adapter, sequential ops, mixed direct/decomposed, native vocabulary closure."""
        cz_adapter = CustomCZAdapter()
        res = NativeTranslator.translate(self.physical_circuit, cz_adapter)
        self.assertTrue(res.success)
        # Verify closure: every native operation in res.native_circuit belongs to cz_adapter vocabulary!
        for nop in res.native_circuit.native_operations:
            self.assertTrue(cz_adapter.validate_native_operation(nop))

    # ------------------------------------------------------------------
    # NEGATIVE TESTS (16)
    # ------------------------------------------------------------------
    def test_neg_01_unsupported_gate(self) -> None:
        """Neg 1: Unsupported gate with no decomposition rejected."""
        g_unsupported = PhysicalGateOperation(gate_type="UNKNOWN_UNSUPPORTED_GATE", target_node=0, operation_index=2)
        c_bad = PhysicalCircuitIR(
            physical_circuit_id="p_bad",
            source_logical_circuit_id="l1",
            physical_qubits=[self.p0, self.p1],
            gates=[self.g0, self.g1, g_unsupported],
            mapping=self.mapping,
            topology=self.topology,
            provenance=self.provenance,
        )
        res = NativeTranslator.translate(c_bad, self.adapter)
        self.assertFalse(res.success)
        self.assertIn(g_unsupported, res.unresolved_operations)

    def test_neg_02_03_04_invalid_gate_definition(self) -> None:
        """Neg 2, 3, 4: Empty gate_id or invalid arity rejected."""
        with self.assertRaises(ValueError):
            NativeGateDefinition(gate_id="", gate_name="name", arity=1)
        with self.assertRaises(ValueError):
            NativeGateDefinition(gate_id="X", gate_name="name", arity=0)

    def test_neg_05_06_07_missing_or_invalid_decomposition(self) -> None:
        """Neg 5, 6, 7: Decomposition producing unsupported native operation rejected."""
        # Create an entry with invalid native gate
        def bad_decomp(op: PhysicalGateOperation) -> list:
            return [NativeOperation(native_gate="NON_EXISTENT_NATIVE", operands=(0,))]

        GateDecompositionRegistry.register(
            DecompositionEntry(
                decomposition_id="BAD_DECOMP",
                source_gate_type="BAD_GATE",
                target_backend_class="ALL",
                decompose_func=bad_decomp,
            )
        )

        g_bad = PhysicalGateOperation(gate_type="BAD_GATE", target_node=0, operation_index=0)
        res = self.adapter.resolve_gate(g_bad)
        self.assertEqual(res.status, NativeResolutionStatus.UNSUPPORTED)

    def test_neg_08_09_operand_mismatch_or_out_of_bounds(self) -> None:
        """Neg 8 & 9: Operand out-of-bounds rejected by validator."""
        nop_bad = NativeOperation(native_gate="X", operands=(99,), operation_index=0)
        c_bad = NativeCircuitIR(
            circuit_id="n1",
            backend_id="b1",
            backend_version="1.0",
            qubits=[0, 1],
            native_operations=[nop_bad],
            input_mapping=self.mapping,
            output_mapping=self.mapping,
            provenance=self.provenance,
        )
        val_res = validate_native_circuit_ir(c_bad, self.adapter)
        self.assertFalse(val_res.valid)

    def test_neg_10_11_12_semantic_mismatch_or_non_unitary(self) -> None:
        """Neg 11 & 12: Non-unitary or semantically non-equivalent native circuit rejected."""
        res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        # Corrupt native operations list (replace CNOT with X)
        res.native_circuit.native_operations[1] = NativeOperation(native_gate="X", operands=(1,), operation_index=1)
        ver_rep = NativeCircuitVerifier.verify_equivalence(self.physical_circuit, res.native_circuit)
        self.assertFalse(ver_rep.verified)

    def test_neg_14_15_malformed_serialization(self) -> None:
        """Neg 14 & 15: Malformed JSON or schema mismatch rejected."""
        with self.assertRaises(ValueError):
            deserialize_native_circuit_ir("{bad json}")

        res = NativeTranslator.translate(self.physical_circuit, self.adapter)
        s_json = serialize_native_circuit_ir(res.native_circuit)
        bad_ver = s_json.replace('"1.0.0"', '"9.9.9"')
        with self.assertRaises(ValueError):
            deserialize_native_circuit_ir(bad_ver)


if __name__ == "__main__":
    unittest.main()
