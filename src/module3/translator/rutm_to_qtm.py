"""
RUTM-IR -> QTM-IR Translator T_RQ (Module 3 Stage 6).

Performs canonical semantic lifting of Reversible Universal Turing Machine (RUTM)
programs and configurations into validated Quantum Turing Machine Intermediate Representation (QTM-IR).
"""

import hashlib
import json
from typing import Dict, List, Tuple, Optional, Set, Any, Union

from src.module1.utm.model import Direction, TransitionAction, UTMProgram
from src.module2.rutm.model import (
    RUTMConfiguration,
    HistoryRecord,
    valid_rutm_configuration,
    create_initial_rutm_configuration,
)
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module2.rutm_ir.model import RUTM_IR
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRBasisState,
    QTMIRStateVector,
    QTMIRTransitionMapping,
    QTMIRMatrixRepresentation,
    QTMIRProvenance,
    QTMIRComplexNumber,
    QTM_IR_VERSION,
    CANONICAL_SEMANTIC_RELATION,
)
from src.module3.qtm_ir.validator import validate_qtm_ir, ValidationResult


class RUTMToQTMTranslationError(ValueError):
    """Raised when RUTM-IR -> QTM-IR translation fails or produces invalid QTM-IR."""
    pass


def compute_canonical_basis_id(config: RUTMConfiguration) -> str:
    """
    Computes a deterministic, collision-free canonical basis ID for RUTM configuration C_R.

    Canonical identity property:
    compute_canonical_basis_id(C1) == compute_canonical_basis_id(C2) iff C1 == C2.
    Participating components: (q, T, h, H, k, halted, error).
    """
    sorted_tape = [(k, config.tape[k]) for k in sorted(config.tape.keys())]

    serialized_history = []
    for rec in config.history:
        if isinstance(rec, HistoryRecord) or hasattr(rec, "prev_state"):
            dir_val = rec.direction.value if hasattr(rec.direction, "value") else str(rec.direction)
            serialized_history.append((rec.prev_state, rec.overwritten_symbol, dir_val))
        elif isinstance(rec, dict):
            serialized_history.append((rec.get("prev_state", ""), rec.get("overwritten_symbol", ""), str(rec.get("direction", ""))))
        else:
            serialized_history.append(str(rec))

    config_tuple = (
        config.current_state,
        tuple(sorted_tape),
        config.head_pos,
        tuple(serialized_history),
        config.step_count,
        config.halted,
        config.error or "",
    )

    raw_str = json.dumps(config_tuple, sort_keys=True)
    hash_digest = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:12]
    return f"b_{config.current_state}_s{config.step_count}_{hash_digest}"


def lift_configuration(config: RUTMConfiguration, basis_id: Optional[str] = None) -> QTMIRBasisState:
    """
    Performs configuration lifting ι(C_R) = |C_R⟩.

    Preserves every semantic component of C_R = (q, T, h, H, k, halted, error).
    """
    b_id = basis_id or compute_canonical_basis_id(config)
    return QTMIRBasisState(
        basis_id=b_id,
        current_state=config.current_state,
        tape=dict(config.tape),
        head_pos=config.head_pos,
        history=config.history,
        step_count=config.step_count,
        halted=config.halted,
        error=config.error,
    )


def compute_source_program_hash(program: Union[RUTM_IR, UTMProgram]) -> str:
    """
    Computes a deterministic SHA-256 hash of source program structure.
    """
    if isinstance(program, RUTM_IR):
        utm_prog = program.to_utm_program()
    elif isinstance(program, UTMProgram):
        utm_prog = program
    else:
        raise TypeError(f"Expected RUTM_IR or UTMProgram, got {type(program).__name__}.")

    sorted_transitions = []
    for (state, sym), action in sorted(utm_prog.transitions.items(), key=lambda x: (x[0][0], str(x[0][1]))):
        dir_val = action.direction.value if hasattr(action.direction, "value") else str(action.direction)
        sorted_transitions.append((state, sym, action.next_state, action.write_symbol, dir_val))

    prog_data = {
        "alphabet": sorted(list(utm_prog.alphabet)),
        "blank_symbol": utm_prog.blank_symbol,
        "halt_state": utm_prog.halt_state,
        "initial_state": utm_prog.initial_state,
        "states": sorted(list(utm_prog.states)),
        "transitions": sorted_transitions,
    }

    raw_json = json.dumps(prog_data, sort_keys=True)
    return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()


class RUTMToQTMTranslator:
    """
    RUTM-IR -> QTM-IR Translator (T_RQ).

    Translates Reversible Universal Turing Machine programs and configurations
    into validated QTM-IR models strictly preserving actual RUTM semantics.
    """

    def __init__(self, machine_id: str = "qtm_instance"):
        self.machine_id = machine_id

    def translate(
        self,
        program: Union[RUTM_IR, UTMProgram],
        initial_config: Optional[RUTMConfiguration] = None,
        initial_tape: Optional[Dict[int, str]] = None,
        max_steps: int = 100,
        custom_domain: Optional[List[RUTMConfiguration]] = None,
        include_matrix: bool = True,
    ) -> QTMIRModel:
        """
        Translates a reversible program and initial configuration / domain into a validated QTMIRModel.

        :param program: RUTM_IR or UTMProgram instance.
        :param initial_config: Optional initial RUTMConfiguration.
        :param initial_tape: Optional initial tape dictionary.
        :param max_steps: Maximum forward steps to trace domain D.
        :param custom_domain: Optional explicit domain of configurations.
        :param include_matrix: Whether to construct finite matrix representation [U_P].
        :return: Validated QTMIRModel instance.
        """
        if isinstance(program, RUTM_IR):
            utm_prog = program.to_utm_program()
        elif isinstance(program, UTMProgram):
            utm_prog = program
        else:
            raise RUTMToQTMTranslationError(f"Unsupported program type: {type(program).__name__}")

        # 1. Determine Initial Configuration C_0
        if initial_config is not None:
            c0 = initial_config
        elif custom_domain is not None and len(custom_domain) > 0:
            c0 = custom_domain[0]
        else:
            tape = initial_tape if initial_tape is not None else {}
            c0 = create_initial_rutm_configuration(tape, utm_prog.initial_state)

        # Validate initial configuration
        is_valid_c0, err_c0 = valid_rutm_configuration(c0, utm_prog.states, utm_prog.alphabet, utm_prog.halt_state)
        if not is_valid_c0:
            raise RUTMToQTMTranslationError(f"Initial configuration is invalid: {err_c0}")

        # 2. Construct Domain D
        domain_configs: List[RUTMConfiguration] = []
        domain_b_ids: Set[str] = set()

        if custom_domain is not None:
            domain_configs = list(custom_domain)
            for cfg in domain_configs:
                is_valid, err = valid_rutm_configuration(cfg, utm_prog.states, utm_prog.alphabet, utm_prog.halt_state)
                if not is_valid:
                    raise RUTMToQTMTranslationError(f"Custom domain configuration is invalid: {err}")
                b_id = compute_canonical_basis_id(cfg)
                domain_b_ids.add(b_id)
        else:
            # Trace execution up to max_steps or halting
            curr = c0
            domain_configs.append(curr)
            domain_b_ids.add(compute_canonical_basis_id(curr))
            steps = 0
            while steps < max_steps and not curr.halted and curr.current_state != utm_prog.halt_state and curr.error is None:
                next_c = forward_step_rutm(curr, utm_prog)
                if next_c.error is not None:
                    raise RUTMToQTMTranslationError(f"Error during forward execution step: {next_c.error}")

                next_b_id = compute_canonical_basis_id(next_c)
                if next_b_id in domain_b_ids:
                    break
                domain_configs.append(next_c)
                domain_b_ids.add(next_b_id)
                curr = next_c
                steps += 1

        # 3. Lift Configurations to QTMIRBasisState
        basis_states: Dict[str, QTMIRBasisState] = {}
        config_by_b_id: Dict[str, RUTMConfiguration] = {}

        for cfg in domain_configs:
            b_id = compute_canonical_basis_id(cfg)
            b_state = lift_configuration(cfg, b_id)

            if b_id in basis_states and basis_states[b_id] != b_state:
                raise RUTMToQTMTranslationError(f"Configuration identity collision detected for basis ID '{b_id}'.")

            basis_states[b_id] = b_state
            config_by_b_id[b_id] = cfg

        N = len(domain_configs)
        if N == 0:
            raise RUTMToQTMTranslationError("Domain D must not be empty.")

        # 4. Build Forward and Reverse Transition Mappings strictly using ACTUAL RUTM semantics (zero fallbacks/fabrication)
        forward_mapping: Dict[str, str] = {}
        reverse_mapping: Dict[str, str] = {}
        seen_targets: Set[str] = set()

        for src_id, cfg in config_by_b_id.items():
            if cfg.error is not None or cfg.halted or cfg.current_state == utm_prog.halt_state:
                tgt_cfg = cfg
            else:
                tgt_cfg = forward_step_rutm(cfg, utm_prog)
                if tgt_cfg.error is not None:
                    raise RUTMToQTMTranslationError(f"Forward step error for state '{cfg.current_state}': {tgt_cfg.error}")

            tgt_id = compute_canonical_basis_id(tgt_cfg)

            # Strict Domain Closure Check: Actual target MUST be in domain D
            if tgt_id not in config_by_b_id:
                raise RUTMToQTMTranslationError(
                    f"Domain closure failure: Forward transition R_P from configuration '{src_id}' produced target configuration '{tgt_id}' not in domain D."
                )

            # Strict Injectivity Check: No forward target collisions
            if tgt_id in seen_targets and forward_mapping.get(src_id) != tgt_id:
                for prev_src, prev_tgt in forward_mapping.items():
                    if prev_tgt == tgt_id and prev_src != src_id:
                        raise RUTMToQTMTranslationError(
                            f"Non-bijective forward transition: Sources '{prev_src}' and '{src_id}' both map to target '{tgt_id}' (collision)."
                        )

            forward_mapping[src_id] = tgt_id
            seen_targets.add(tgt_id)

        # Actual reverse step R_P^-1(C') using Module 2 reverse_step_rutm semantics directly
        for tgt_id, cfg in config_by_b_id.items():
            if cfg.error is not None:
                rev_src_cfg = cfg
            elif (cfg.halted or cfg.current_state == utm_prog.halt_state) and len(cfg.history) == 0:
                rev_src_cfg = cfg
            else:
                rev_src_cfg = reverse_step_rutm(cfg, utm_prog)

            rev_src_id = compute_canonical_basis_id(rev_src_cfg)

            # Domain closure check for reverse step
            if rev_src_id not in config_by_b_id:
                raise RUTMToQTMTranslationError(
                    f"Domain closure failure: Reverse transition R_P^-1 from target '{tgt_id}' produced predecessor configuration '{rev_src_id}' not in domain D."
                )

            reverse_mapping[tgt_id] = rev_src_id

        # Strict Totality & Surjectivity Verification
        domain_ids = set(basis_states.keys())
        if set(forward_mapping.keys()) != domain_ids:
            raise RUTMToQTMTranslationError("Forward mapping is not total over domain D.")
        if set(forward_mapping.values()) != domain_ids:
            raise RUTMToQTMTranslationError("Forward mapping is not surjective over domain D.")
        if set(reverse_mapping.keys()) != domain_ids:
            raise RUTMToQTMTranslationError("Reverse mapping is not total over domain D.")
        if set(reverse_mapping.values()) != domain_ids:
            raise RUTMToQTMTranslationError("Reverse mapping is not surjective over domain D.")

        # Strict Inverse Composition Identities: R_P^-1 ∘ R_P = id_D and R_P ∘ R_P^-1 = id_D
        for b_id in domain_ids:
            if reverse_mapping[forward_mapping[b_id]] != b_id:
                raise RUTMToQTMTranslationError(f"Composition failure R_P^-1 ∘ R_P != id_D at '{b_id}'.")
            if forward_mapping[reverse_mapping[b_id]] != b_id:
                raise RUTMToQTMTranslationError(f"Composition failure R_P ∘ R_P^-1 != id_D at '{b_id}'.")

        trans_mapping = QTMIRTransitionMapping(
            forward_mapping=forward_mapping,
            reverse_mapping=reverse_mapping,
            is_bijective=True,
        )

        # 5. Lift Initial State Vector
        c0_id = compute_canonical_basis_id(c0)
        init_vector = QTMIRStateVector(
            amplitudes={c0_id: QTMIRComplexNumber(1.0, 0.0)},
            tolerance=1e-12,
            is_normalized=True,
        )

        # 6. Build Finite Matrix Representation strictly matching ACTUAL R_P
        matrix_rep = None
        if include_matrix:
            basis_order = sorted(list(basis_states.keys()))
            basis_index_map = {b_id: idx for idx, b_id in enumerate(basis_order)}

            c0_complex = QTMIRComplexNumber(0.0, 0.0)
            c1_complex = QTMIRComplexNumber(1.0, 0.0)

            matrix = [[c0_complex for _ in range(N)] for _ in range(N)]
            for col_idx, src_b_id in enumerate(basis_order):
                tgt_b_id = forward_mapping[src_b_id]
                row_idx = basis_index_map[tgt_b_id]
                matrix[row_idx][col_idx] = c1_complex

            matrix_rep = QTMIRMatrixRepresentation(
                basis_order=basis_order,
                matrix=matrix,
                dimension=N,
            )

        # 7. Build Provenance
        prog_hash = compute_source_program_hash(program)
        provenance = QTMIRProvenance(
            source_rutm_program_hash=prog_hash,
            source_module="Module 2 (RUTM-IR)",
            stage="Stage 6 (Translator T_RQ)",
            compiler_version="0.3.0-alpha",
            semantic_relation=CANONICAL_SEMANTIC_RELATION,
        )

        # 8. Assemble QTMIRModel
        model = QTMIRModel(
            version=QTM_IR_VERSION,
            machine_id=self.machine_id,
            basis_states=basis_states,
            initial_state_vector=init_vector,
            transition_mapping=trans_mapping,
            matrix_representation=matrix_rep,
            provenance=provenance,
        )

        # 9. Validation Gate
        val_res = validate_qtm_ir(model)
        if not val_res.valid:
            errors = [d.message for d in val_res.diagnostics]
            raise RUTMToQTMTranslationError(f"QTM-IR validation failed after translation: {errors}")

        return model


def translate_rutm_to_qtm_ir(
    program: Union[RUTM_IR, UTMProgram],
    initial_config: Optional[RUTMConfiguration] = None,
    initial_tape: Optional[Dict[int, str]] = None,
    max_steps: int = 100,
    custom_domain: Optional[List[RUTMConfiguration]] = None,
    machine_id: str = "qtm_instance",
    include_matrix: bool = True,
) -> QTMIRModel:
    """
    Convenience API function executing RUTM-IR -> QTM-IR translation (T_RQ).
    """
    translator = RUTMToQTMTranslator(machine_id=machine_id)
    return translator.translate(
        program=program,
        initial_config=initial_config,
        initial_tape=initial_tape,
        max_steps=max_steps,
        custom_domain=custom_domain,
        include_matrix=include_matrix,
    )


def verify_forward_commuting_relation(
    model: QTMIRModel,
    program: Union[RUTM_IR, UTMProgram],
    domain_configs: List[RUTMConfiguration],
) -> bool:
    """
    Executes operational verification of U_P ∘ ι = ι ∘ R_P.
    For each C in D, verifies translated forward mapping matches ACTUAL iota(R_P(C)).
    """
    if isinstance(program, RUTM_IR):
        utm_prog = program.to_utm_program()
    else:
        utm_prog = program

    f_map = model.transition_mapping.forward_mapping
    for cfg in domain_configs:
        src_id = compute_canonical_basis_id(cfg)
        if src_id not in f_map:
            return False

        if cfg.error is not None or cfg.halted or cfg.current_state == utm_prog.halt_state:
            expected_next_cfg = cfg
        else:
            expected_next_cfg = forward_step_rutm(cfg, utm_prog)

        expected_next_id = compute_canonical_basis_id(expected_next_cfg)
        if f_map[src_id] != expected_next_id:
            return False

    return True


def verify_reverse_commuting_relation(
    model: QTMIRModel,
    program: Union[RUTM_IR, UTMProgram],
    domain_configs: List[RUTMConfiguration],
) -> bool:
    """
    Executes operational verification of U_P^† ∘ ι = ι ∘ R_P^-1.
    For each C' in D, verifies translated reverse mapping matches ACTUAL iota(R_P^-1(C')).
    """
    if isinstance(program, RUTM_IR):
        utm_prog = program.to_utm_program()
    else:
        utm_prog = program

    r_map = model.transition_mapping.reverse_mapping
    for cfg in domain_configs:
        tgt_id = compute_canonical_basis_id(cfg)
        if tgt_id not in r_map:
            return False

        if cfg.error is not None:
            expected_prev_cfg = cfg
        elif (cfg.halted or cfg.current_state == utm_prog.halt_state) and len(cfg.history) == 0:
            expected_prev_cfg = cfg
        else:
            expected_prev_cfg = reverse_step_rutm(cfg, utm_prog)

        expected_prev_id = compute_canonical_basis_id(expected_prev_cfg)
        if r_map[tgt_id] != expected_prev_id:
            return False

    return True
