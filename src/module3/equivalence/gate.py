"""
Reversible -> Quantum Equivalence Verification Gate (Module 3 Stage 8).

Independently executes Module 2 reversible path (R_P) and Module 3 QTM execution path (U_P)
to verify exact semantic correspondence iota(R_P^t(C_0)) = U_P^t |C_0> for all t in [0 ... T].
"""

from typing import Optional, Union, Any, List
import math

from src.module1.utm.model import UTMProgram
from src.module2.rutm.model import (
    RUTMConfiguration,
    create_initial_rutm_configuration,
)
from src.module2.rutm.semantics import (
    forward_step_rutm,
    reverse_step_rutm,
)
from src.module2.rutm_ir.model import RUTM_IR
from src.module3.qtm import iota
from src.module3.qtm_ir.model import (
    QTMIRModel,
    QTMIRStateVector,
    QTMIRComplexNumber,
    QTMIRProvenance,
)
from src.module3.qtm_ir.validator import validate_qtm_ir
from src.module3.translator import (
    compute_canonical_basis_id,
)
from src.module3.execution import (
    apply_unitary,
    apply_adjoint,
    QTMExecutionError,
)
from src.module3.equivalence.result import (
    EquivalenceStatus,
    EquivalenceStepResult,
    EquivalenceResult,
)


def _canonical_id_from_basis_state(b_state: Any) -> str:
    """Helper constructing canonical basis ID directly from QTMIRBasisState fields."""
    cfg = RUTMConfiguration(
        current_state=b_state.current_state,
        tape=dict(b_state.tape),
        head_pos=b_state.head_pos,
        history=b_state.history,
        step_count=b_state.step_count,
        halted=b_state.halted,
        error=b_state.error,
    )
    return compute_canonical_basis_id(cfg)


def verify_equivalence(
    rutm_program: Union[RUTM_IR, UTMProgram, Any],
    qtm_ir: QTMIRModel,
    initial_config: Optional[RUTMConfiguration] = None,
    max_steps: int = 5,
    verify_reverse: bool = False,
) -> EquivalenceResult:
    """
    Independently verifies step-by-step equivalence iota(R_P^t(C_0)) = U_P^t |C_0> across horizon T.

    :param rutm_program: Source RUTM_IR or UTMProgram instance.
    :param qtm_ir: Target validated QTMIRModel instance.
    :param initial_config: Optional initial RUTMConfiguration C_0 (resolved automatically if None).
    :param max_steps: Verification horizon T (>= 0).
    :param verify_reverse: If True, also performs reverse adjoint equivalence check.
    :return: EquivalenceResult with three-valued outcome (PASS / FAIL / INCONCLUSIVE).
    """
    prov = qtm_ir.provenance

    # 1. Horizon validation
    if max_steps < 0:
        return EquivalenceResult(
            status=EquivalenceStatus.INCONCLUSIVE,
            max_steps=max_steps,
            verified_steps=0,
            first_failure_step=None,
            diagnostics=[f"Invalid verification horizon max_steps = {max_steps} < 0."],
            provenance=prov,
        )

    # 2. QTM-IR model validation boundary
    val_res = validate_qtm_ir(qtm_ir)
    if not val_res.valid:
        errs = [d.message for d in val_res.diagnostics]
        return EquivalenceResult(
            status=EquivalenceStatus.INCONCLUSIVE,
            max_steps=max_steps,
            verified_steps=0,
            first_failure_step=None,
            diagnostics=[f"QTM-IR validation gate failed: {errs}"],
            provenance=prov,
        )

    # 3. Resolve UTMProgram contract for Module 2 execution
    if isinstance(rutm_program, RUTM_IR):
        utm_prog = UTMProgram(
            states=rutm_program.states,
            alphabet=rutm_program.tape_alphabet,
            blank_symbol=rutm_program.blank_symbol,
            initial_state=rutm_program.initial_state,
            halt_state=rutm_program.halt_state,
            transitions=rutm_program.transitions,
        )
    elif isinstance(rutm_program, UTMProgram):
        utm_prog = rutm_program
    else:
        return EquivalenceResult(
            status=EquivalenceStatus.INCONCLUSIVE,
            max_steps=max_steps,
            verified_steps=0,
            first_failure_step=None,
            diagnostics=[f"Unsupported rutm_program type: {type(rutm_program)}"],
            provenance=prov,
        )

    # 4. Resolve initial configuration C_0
    if initial_config is not None:
        c_curr = initial_config
    else:
        # Resolve from qtm_ir initial state vector if possible
        v_init = qtm_ir.initial_state_vector
        active_inits = [b_id for b_id, amp in v_init.amplitudes.items() if amp.abs() > v_init.tolerance]
        if len(active_inits) == 1 and active_inits[0] in qtm_ir.basis_states:
            b_state = qtm_ir.basis_states[active_inits[0]]
            c_curr = RUTMConfiguration(
                current_state=b_state.current_state,
                tape=dict(b_state.tape),
                head_pos=b_state.head_pos,
                history=b_state.history,
                step_count=b_state.step_count,
                halted=b_state.halted,
                error=b_state.error,
            )
        else:
            c_curr = create_initial_rutm_configuration({}, utm_prog.initial_state)

    q_curr = qtm_ir.initial_state_vector

    trace: List[EquivalenceStepResult] = []

    # 5. Step-by-step forward verification loop t = 0 ... max_steps
    for t in range(max_steps + 1):
        if t > 0:
            # Independent Path A: Reversible execution via Module 2
            c_curr = forward_step_rutm(c_curr, utm_prog)

            # Independent Path B: Quantum execution via Module 3 Stage 7
            try:
                q_curr = apply_unitary(qtm_ir, q_curr)
            except Exception as e:
                return EquivalenceResult(
                    status=EquivalenceStatus.FAIL,
                    max_steps=max_steps,
                    verified_steps=t - 1,
                    first_failure_step=t,
                    trace=trace,
                    diagnostics=[f"Quantum execution error at step {t}: {e}"],
                    provenance=prov,
                )

        # Expected canonical basis ID for C_t
        exp_basis_id = compute_canonical_basis_id(c_curr)

        # Domain inclusion check
        if exp_basis_id not in qtm_ir.basis_states:
            step_res = EquivalenceStepResult(
                step=t,
                classical_configuration=c_curr,
                expected_basis_id=exp_basis_id,
                quantum_state=q_curr,
                support_match=False,
                amplitude_match=False,
                identity_match=False,
                status=EquivalenceStatus.INCONCLUSIVE,
                classical_transition=f"R_P -> {c_curr.current_state}",
                quantum_transition=f"U_P -> domain_missing",
                diagnostics=[f"Step {t}: Classical configuration '{exp_basis_id}' not in QTM-IR domain D."],
            )
            trace.append(step_res)
            return EquivalenceResult(
                status=EquivalenceStatus.INCONCLUSIVE,
                max_steps=max_steps,
                verified_steps=t,
                first_failure_step=t,
                trace=trace,
                diagnostics=[f"Domain truncation / mismatch at step {t}: Reversible configuration '{exp_basis_id}' not in QTM-IR domain D."],
                provenance=prov,
            )

        # Evaluate quantum state support and amplitudes
        tol = q_curr.tolerance
        active_amps = {b_id: amp for b_id, amp in q_curr.amplitudes.items() if amp.abs() > tol}

        support_match = (set(active_amps.keys()) == {exp_basis_id})

        exp_amp = q_curr.amplitudes.get(exp_basis_id, QTMIRComplexNumber(0.0, 0.0))
        amplitude_match = (
            abs(exp_amp.real - 1.0) <= tol and abs(exp_amp.imag - 0.0) <= tol and len(active_amps) == 1
        )

        # Independent Witness Identity Check: Re-verify that qtm_ir.basis_states[exp_basis_id] matches C_t
        qtm_basis_state = qtm_ir.basis_states.get(exp_basis_id)
        identity_match = (
            (exp_basis_id in q_curr.amplitudes)
            and (qtm_basis_state is not None)
            and (_canonical_id_from_basis_state(qtm_basis_state) == exp_basis_id)
        )

        step_status = EquivalenceStatus.PASS if (support_match and amplitude_match and identity_match) else EquivalenceStatus.FAIL

        step_diag: List[str] = []
        if not support_match:
            step_diag.append(f"Support mismatch: expected {{{exp_basis_id}}}, got {set(active_amps.keys())}.")
        if not amplitude_match:
            step_diag.append(f"Amplitude mismatch for '{exp_basis_id}': expected 1.0+0.0j, got {exp_amp.real}+{exp_amp.imag}j.")
        if not identity_match:
            step_diag.append(f"Identity mismatch for '{exp_basis_id}'.")

        step_res = EquivalenceStepResult(
            step=t,
            classical_configuration=c_curr,
            expected_basis_id=exp_basis_id,
            quantum_state=q_curr,
            support_match=support_match,
            amplitude_match=amplitude_match,
            identity_match=identity_match,
            status=step_status,
            classical_transition=f"R_P -> state={c_curr.current_state}",
            quantum_transition=f"U_P -> support={list(active_amps.keys())}",
            diagnostics=step_diag,
        )
        trace.append(step_res)

        if step_status == EquivalenceStatus.FAIL:
            return EquivalenceResult(
                status=EquivalenceStatus.FAIL,
                max_steps=max_steps,
                verified_steps=t,
                first_failure_step=t,
                trace=trace,
                diagnostics=[f"First divergence observed at step {t}: {step_diag}"],
                provenance=prov,
            )

    # 6. Optional reverse equivalence check (U_P^dagger iota(C_t) = iota(R_P^-1(C_t)))
    if verify_reverse and max_steps > 0:
        c_rev = c_curr
        q_rev = q_curr
        for r_step in range(max_steps, 0, -1):
            c_rev = reverse_step_rutm(c_rev, utm_prog)
            try:
                q_rev = apply_adjoint(qtm_ir, q_rev)
            except Exception as e:
                return EquivalenceResult(
                    status=EquivalenceStatus.FAIL,
                    max_steps=max_steps,
                    verified_steps=max_steps,
                    first_failure_step=r_step - 1,
                    trace=trace,
                    diagnostics=[f"Reverse quantum execution error at step {r_step - 1}: {e}"],
                    provenance=prov,
                )

            exp_rev_id = compute_canonical_basis_id(c_rev)
            active_rev = {b_id: amp for b_id, amp in q_rev.amplitudes.items() if amp.abs() > q_rev.tolerance}

            if set(active_rev.keys()) != {exp_rev_id} or abs(q_rev.amplitudes.get(exp_rev_id, QTMIRComplexNumber(0, 0)).real - 1.0) > q_rev.tolerance:
                return EquivalenceResult(
                    status=EquivalenceStatus.FAIL,
                    max_steps=max_steps,
                    verified_steps=max_steps,
                    first_failure_step=r_step - 1,
                    trace=trace,
                    diagnostics=[f"Reverse equivalence divergence at step {r_step - 1}."],
                    provenance=prov,
                )

    return EquivalenceResult(
        status=EquivalenceStatus.PASS,
        max_steps=max_steps,
        verified_steps=max_steps + 1,
        first_failure_step=None,
        trace=trace,
        diagnostics=["Equivalence verified across all steps."],
        provenance=prov,
    )


class EquivalenceGate:
    """
    Object-oriented Equivalence Verification Gate.
    """

    def __init__(self, rutm_program: Union[RUTM_IR, UTMProgram, Any], qtm_ir: QTMIRModel):
        self.rutm_program = rutm_program
        self.qtm_ir = qtm_ir

    def verify(
        self,
        initial_config: Optional[RUTMConfiguration] = None,
        max_steps: int = 5,
        verify_reverse: bool = False,
    ) -> EquivalenceResult:
        """Runs independent step-by-step equivalence verification."""
        return verify_equivalence(
            rutm_program=self.rutm_program,
            qtm_ir=self.qtm_ir,
            initial_config=initial_config,
            max_steps=max_steps,
            verify_reverse=verify_reverse,
        )
