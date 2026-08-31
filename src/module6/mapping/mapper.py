"""
Module 6 Stage 1 — Compiler Mapping Observer.

Observes the compiler-induced mapping F : A_C -> C_Q^logical by executing the frozen
Module 1-4 synthesis pipeline (RUTM -> QTM-IR -> QuantumCircuitIR -> Decomposed Circuit-IR).
"""

from typing import Dict, Optional
from src.module1.utm.model import UTMProgram
from src.module3.translator import translate_rutm_to_qtm_ir
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module4.synthesis import synthesize_qtm_transition
from src.module4.decomposition.decomposer import decompose_circuit_ir
from src.module6.classical.semantic import ClassicalSemanticModel


class CompilerMapper:
    """
    Observer for compiler-induced mapping F : A_C -> C_Q^logical.
    """

    @classmethod
    def map_classical_model(
        cls,
        model: ClassicalSemanticModel,
        program: UTMProgram,
        circuit_id: Optional[str] = None,
    ) -> QuantumCircuitIR:
        """
        Executes frozen Module 1-4 synthesis to produce logical QuantumCircuitIR F(A).
        """
        # 1. Translate to QTM-IR using domain from model
        qtm_ir = translate_rutm_to_qtm_ir(
            program=program,
            custom_domain=model.domain_contract.domain,
        )

        # 2. Synthesize Stage 3 QuantumCircuitIR
        stage3_circuit = synthesize_qtm_transition(
            program=program,
            qtm_ir=qtm_ir,
            domain_contract=model.domain_contract,
            encoding_spec=model.encoding_spec,
            state_map=model.state_map,
            symbol_map=model.symbol_map,
            circuit_id=circuit_id or f"stage3_{model.algorithm_id}",
        )

        # 3. Decompose to Stage 4 Primitive QuantumCircuitIR (X, CNOT, TOFFOLI)
        stage4_circuit = decompose_circuit_ir(
            circuit=stage3_circuit,
            circuit_id=circuit_id or f"logical_{model.algorithm_id}",
        )

        return stage4_circuit
