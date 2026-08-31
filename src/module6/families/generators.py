"""
Module 6 Stage 2 — Deterministic Classical Algorithm Family Generators.

Constructs controlled, finite families A_N subset A_C of valid classical semantic models (ClassicalSemanticModel)
and UTM programs strictly compliant with Modules 1-5 frozen semantics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
import hashlib
from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module4 import FiniteDomainContract
from src.module6.classical.semantic import ClassicalSemanticModel
from src.module6.classical.transition import build_classical_semantic_model


@dataclass(frozen=True)
class AlgorithmFamily:
    """
    Immutable representation of a generated algorithm family A_N subset A_C.
    """
    family_id: str
    parameter_tuple: Tuple[Any, ...]
    semantic_signature: str
    models: Tuple[ClassicalSemanticModel, ...]
    programs: Tuple[UTMProgram, ...]


class AlgorithmFamilyGenerator:
    """
    Deterministic generator for finite classical algorithm families.
    """

    @classmethod
    def generate_family(
        cls,
        family_id: str,
        size: int = 3,
        parameter_tuple: Tuple[Any, ...] = (),
    ) -> AlgorithmFamily:
        """
        Generates an algorithm family by ID.
        
        Supported family IDs:
        - "identity_family"
        - "bit_flip_family"
        - "two_state_cycle_family"
        - "multi_state_cycle_family"
        - "controlled_transition_family"
        - "reversible_permutation_family"
        """
        if size <= 0:
            raise ValueError(f"Family size must be positive, got {size}")

        if family_id == "identity_family":
            return cls._generate_identity_family(size, parameter_tuple)
        elif family_id == "bit_flip_family":
            return cls._generate_bit_flip_family(size, parameter_tuple)
        elif family_id == "two_state_cycle_family":
            return cls._generate_two_state_cycle_family(size, parameter_tuple)
        elif family_id == "multi_state_cycle_family":
            return cls._generate_multi_state_cycle_family(size, parameter_tuple)
        elif family_id == "controlled_transition_family":
            return cls._generate_controlled_family(size, parameter_tuple)
        elif family_id == "reversible_permutation_family":
            return cls._generate_permutation_family(size, parameter_tuple)
        else:
            raise ValueError(f"Unknown algorithm family ID: '{family_id}'")

    @classmethod
    def _generate_identity_family(
        cls, size: int, parameter_tuple: Tuple[Any, ...]
    ) -> AlgorithmFamily:
        models: List[ClassicalSemanticModel] = []
        programs: List[UTMProgram] = []

        for i in range(size):
            prog = UTMProgram(
                states={"q0", "q_halt"},
                alphabet={"0", "1", "_"},
                blank_symbol="_",
                initial_state="q0",
                halt_state="q_halt",
                transitions={
                    ("q0", "0"): TransitionAction("q_halt", "0", Direction.RIGHT),
                },
            )
            # Create halted configurations with valid alphabet symbols ("0", "1", "_")
            configs = [
                RUTMConfiguration(
                    current_state="q_halt",
                    tape={pos: "1" for pos in range(j + 1)},
                    head_pos=j,
                    step_count=0,
                    halted=True,
                )
                for j in range(i + 1)
            ]
            domain_contract = FiniteDomainContract(domain=configs, execution_horizon=1, initial_configuration=configs[0])
            state_map = {"q0": 0, "q_halt": 1}
            symbol_map = {"_": 0, "0": 1, "1": 2}

            model = build_classical_semantic_model(
                prog, domain_contract, state_map, symbol_map, algorithm_id=f"identity_{i}"
            )
            models.append(model)
            programs.append(prog)

        sig_raw = f"identity_family|{size}|{parameter_tuple}"
        sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()
        return AlgorithmFamily("identity_family", parameter_tuple, sig, tuple(models), tuple(programs))

    @classmethod
    def _generate_bit_flip_family(
        cls, size: int, parameter_tuple: Tuple[Any, ...]
    ) -> AlgorithmFamily:
        models: List[ClassicalSemanticModel] = []
        programs: List[UTMProgram] = []

        for i in range(size):
            prog = UTMProgram(
                states={"q0", "q1", "q_halt"},
                alphabet={"0", "1", "_"},
                blank_symbol="_",
                initial_state="q0",
                halt_state="q_halt",
                transitions={
                    ("q0", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                    ("q1", "0"): TransitionAction("q_halt", "1", Direction.RIGHT),
                },
            )
            configs = [
                RUTMConfiguration(
                    current_state="q_halt",
                    tape={pos: "1" for pos in range(k + 1)},
                    head_pos=k,
                    step_count=0,
                    halted=True,
                )
                for k in range(i + 1)
            ]
            domain_contract = FiniteDomainContract(domain=configs, execution_horizon=1, initial_configuration=configs[0])
            state_map = {"q0": 0, "q1": 1, "q_halt": 2}
            symbol_map = {"_": 0, "0": 1, "1": 2}

            model = build_classical_semantic_model(
                prog, domain_contract, state_map, symbol_map, algorithm_id=f"bit_flip_{i}"
            )
            models.append(model)
            programs.append(prog)

        sig_raw = f"bit_flip_family|{size}|{parameter_tuple}"
        sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()
        return AlgorithmFamily("bit_flip_family", parameter_tuple, sig, tuple(models), tuple(programs))

    @classmethod
    def _generate_two_state_cycle_family(
        cls, size: int, parameter_tuple: Tuple[Any, ...]
    ) -> AlgorithmFamily:
        models: List[ClassicalSemanticModel] = []
        programs: List[UTMProgram] = []

        for i in range(size):
            prog = UTMProgram(
                states={"q0", "q1", "q_halt"},
                alphabet={"0", "1", "_"},
                blank_symbol="_",
                initial_state="q0",
                halt_state="q_halt",
                transitions={
                    ("q0", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                    ("q1", "1"): TransitionAction("q_halt", "0", Direction.LEFT),
                },
            )
            configs = [
                RUTMConfiguration(
                    current_state="q_halt",
                    tape={pos: "1" for pos in range(k + 1)},
                    head_pos=k,
                    step_count=0,
                    halted=True,
                )
                for k in range(i + 1)
            ]
            domain_contract = FiniteDomainContract(domain=configs, execution_horizon=1, initial_configuration=configs[0])
            state_map = {"q0": 0, "q1": 1, "q_halt": 2}
            symbol_map = {"_": 0, "0": 1, "1": 2}

            model = build_classical_semantic_model(
                prog, domain_contract, state_map, symbol_map, algorithm_id=f"two_state_{i}"
            )
            models.append(model)
            programs.append(prog)

        sig_raw = f"two_state_cycle_family|{size}|{parameter_tuple}"
        sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()
        return AlgorithmFamily("two_state_cycle_family", parameter_tuple, sig, tuple(models), tuple(programs))

    @classmethod
    def _generate_multi_state_cycle_family(
        cls, size: int, parameter_tuple: Tuple[Any, ...]
    ) -> AlgorithmFamily:
        models: List[ClassicalSemanticModel] = []
        programs: List[UTMProgram] = []

        for i in range(size):
            prog = UTMProgram(
                states={"q0", "q1", "q2", "q_halt"},
                alphabet={"0", "1", "_"},
                blank_symbol="_",
                initial_state="q0",
                halt_state="q_halt",
                transitions={
                    ("q0", "0"): TransitionAction("q1", "1", Direction.RIGHT),
                    ("q1", "1"): TransitionAction("q2", "0", Direction.RIGHT),
                    ("q2", "0"): TransitionAction("q_halt", "1", Direction.LEFT),
                },
            )
            configs = [
                RUTMConfiguration(
                    current_state="q_halt",
                    tape={pos: "1" for pos in range(k + 1)},
                    head_pos=k,
                    step_count=0,
                    halted=True,
                )
                for k in range(i + 1)
            ]
            domain_contract = FiniteDomainContract(domain=configs, execution_horizon=1, initial_configuration=configs[0])
            state_map = {"q0": 0, "q1": 1, "q2": 2, "q_halt": 3}
            symbol_map = {"_": 0, "0": 1, "1": 2}

            model = build_classical_semantic_model(
                prog, domain_contract, state_map, symbol_map, algorithm_id=f"multi_state_{i}"
            )
            models.append(model)
            programs.append(prog)

        sig_raw = f"multi_state_cycle_family|{size}|{parameter_tuple}"
        sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()
        return AlgorithmFamily("multi_state_cycle_family", parameter_tuple, sig, tuple(models), tuple(programs))

    @classmethod
    def _generate_controlled_family(
        cls, size: int, parameter_tuple: Tuple[Any, ...]
    ) -> AlgorithmFamily:
        models: List[ClassicalSemanticModel] = []
        programs: List[UTMProgram] = []

        for i in range(size):
            prog = UTMProgram(
                states={"q0", "q1", "q_halt"},
                alphabet={"0", "1", "_"},
                blank_symbol="_",
                initial_state="q0",
                halt_state="q_halt",
                transitions={
                    ("q0", "1"): TransitionAction("q1", "0", Direction.RIGHT),
                    ("q1", "0"): TransitionAction("q_halt", "1", Direction.RIGHT),
                },
            )
            configs = [
                RUTMConfiguration(
                    current_state="q_halt",
                    tape={pos: "1" for pos in range(k + 1)},
                    head_pos=k,
                    step_count=0,
                    halted=True,
                )
                for k in range(i + 1)
            ]
            domain_contract = FiniteDomainContract(domain=configs, execution_horizon=1, initial_configuration=configs[0])
            state_map = {"q0": 0, "q1": 1, "q_halt": 2}
            symbol_map = {"_": 0, "0": 1, "1": 2}

            model = build_classical_semantic_model(
                prog, domain_contract, state_map, symbol_map, algorithm_id=f"controlled_{i}"
            )
            models.append(model)
            programs.append(prog)

        sig_raw = f"controlled_family|{size}|{parameter_tuple}"
        sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()
        return AlgorithmFamily("controlled_transition_family", parameter_tuple, sig, tuple(models), tuple(programs))

    @classmethod
    def _generate_permutation_family(
        cls, size: int, parameter_tuple: Tuple[Any, ...]
    ) -> AlgorithmFamily:
        models: List[ClassicalSemanticModel] = []
        programs: List[UTMProgram] = []

        for i in range(size):
            prog = UTMProgram(
                states={"q0", "q_halt"},
                alphabet={"0", "1", "_"},
                blank_symbol="_",
                initial_state="q0",
                halt_state="q_halt",
                transitions={
                    ("q0", "0"): TransitionAction("q_halt", "1", Direction.RIGHT),
                },
            )
            configs = [
                RUTMConfiguration(
                    current_state="q_halt",
                    tape={pos: "1" for pos in range(k + 1)},
                    head_pos=k,
                    step_count=0,
                    halted=True,
                )
                for k in range(i + 1)
            ]
            domain_contract = FiniteDomainContract(domain=configs, execution_horizon=1, initial_configuration=configs[0])
            state_map = {"q0": 0, "q_halt": 1}
            symbol_map = {"_": 0, "0": 1, "1": 2}

            model = build_classical_semantic_model(
                prog, domain_contract, state_map, symbol_map, algorithm_id=f"permutation_{i}"
            )
            models.append(model)
            programs.append(prog)

        sig_raw = f"permutation_family|{size}|{parameter_tuple}"
        sig = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()
        return AlgorithmFamily("reversible_permutation_family", parameter_tuple, sig, tuple(models), tuple(programs))
