"""
Quantum Operational Semantics & Unitary Operator Formulation (Module 3 Stage 3).

Lifts reversible classical transition function R_P : C_R -> C_R into a unitary operator
U_P = Σ |R_P(C)⟩⟨C| operating on Hilbert space H_Q = ℓ²(C_R).

Key Invariants:
1. Basis correspondence: U_P |C_R⟩ = |R_P(C_R)⟩  (U_P ∘ ι = ι ∘ R_P)
2. Linear extension: U_P Σ α_C |C_R⟩ = Σ α_C |R_P(C_R)⟩
3. Adjoint evolution: U_P† |R_P(C_R)⟩ = |C_R⟩  (U_P† ∘ ι = ι ∘ R_P⁻¹)
4. Unitarity invariant: U_P† U_P = U_P U_P† = I (requires R_P total bijection)
5. Norm preservation: ||U_P |ψ⟩|| = |||ψ⟩||
6. Inner-product preservation: ⟨U_P ψ | U_P φ⟩ = ⟨ψ | φ⟩
"""

from typing import Dict, List, Tuple, Callable, Optional, Set, Any
from src.module1.utm.model import UTMProgram
from src.module2.rutm.model import RUTMConfiguration
from src.module2.rutm.semantics import forward_step_rutm, reverse_step_rutm
from src.module3.qtm.basis import QuantumBasisState, iota, basis_inner_product
from src.module3.qtm.state import QTMStateVector, DEFAULT_TOLERANCE


class PermutationMatrixRepresentation:
    """
    Finite N x N matrix representation [U_P] over an ordered finite basis [b_0, b_1, ..., b_{N-1}].
    """

    __slots__ = ("_basis_list", "_matrix", "_size")

    def __init__(
        self,
        basis_list: List[QuantumBasisState],
        matrix: List[List[complex]],
    ) -> None:
        """
        Initializes a finite matrix representation [U_P].

        :param basis_list: Ordered list of unique basis states.
        :param matrix: N x N square complex matrix.
        """
        self._basis_list = list(basis_list)
        self._size = len(basis_list)
        if len(matrix) != self._size or any(len(row) != self._size for row in matrix):
            raise ValueError(f"Matrix dimension must be square {self._size}x{self._size}.")
        self._matrix = [[complex(val) for val in row] for row in matrix]

    @property
    def size(self) -> int:
        """Returns matrix dimension N."""
        return self._size

    @property
    def basis_list(self) -> List[QuantumBasisState]:
        """Returns copy of the ordered basis list."""
        return list(self._basis_list)

    @property
    def matrix(self) -> List[List[complex]]:
        """Returns copy of the 2D complex matrix."""
        return [list(row) for row in self._matrix]

    def is_permutation(self) -> bool:
        """
        Verifies that [U_P] is a valid permutation matrix (exactly one 1.0 per row and column).
        """
        for i in range(self._size):
            row_ones = sum(1 for val in self._matrix[i] if abs(val - 1.0) <= DEFAULT_TOLERANCE)
            row_zeros = sum(1 for val in self._matrix[i] if abs(val) <= DEFAULT_TOLERANCE)
            if row_ones != 1 or (row_ones + row_zeros) != self._size:
                return False

        for j in range(self._size):
            col_ones = sum(1 for i in range(self._size) if abs(self._matrix[i][j] - 1.0) <= DEFAULT_TOLERANCE)
            col_zeros = sum(1 for i in range(self._size) if abs(self._matrix[i][j]) <= DEFAULT_TOLERANCE)
            if col_ones != 1 or (col_ones + col_zeros) != self._size:
                return False

        return True

    def is_unitary(self, tol: float = DEFAULT_TOLERANCE) -> bool:
        """
        Verifies matrix unitarity [U_P]† [U_P] = I AND [U_P] [U_P]† = I.
        """
        N = self._size
        # Compute [U_P]† [U_P]
        for i in range(N):
            for j in range(N):
                val = sum(self._matrix[k][i].conjugate() * self._matrix[k][j] for k in range(N))
                expected = 1.0 if i == j else 0.0
                if abs(val - expected) > tol:
                    return False

        # Compute [U_P] [U_P]†
        for i in range(N):
            for j in range(N):
                val = sum(self._matrix[i][k] * self._matrix[j][k].conjugate() for k in range(N))
                expected = 1.0 if i == j else 0.0
                if abs(val - expected) > tol:
                    return False

        return True


class LiftedUnitaryOperator:
    """
    Representation of lifted unitary transition operator U_P = Σ |R_P(C)⟩⟨C| on H_Q = ℓ²(C_R).

    Requires classical transition functions R_P (forward) and R_P^{-1} (inverse).
    """

    __slots__ = ("_forward_fn", "_reverse_fn", "_name")

    def __init__(
        self,
        forward_fn: Callable[[RUTMConfiguration], RUTMConfiguration],
        reverse_fn: Callable[[RUTMConfiguration], RUTMConfiguration],
        name: str = "U_P",
    ) -> None:
        """
        Initializes a LiftedUnitaryOperator.

        :param forward_fn: Reversible forward transition function R_P(C_R).
        :param reverse_fn: Reversible inverse transition function R_P^{-1}(C_R').
        :param name: Human-readable operator descriptor name.
        """
        if not callable(forward_fn) or not callable(reverse_fn):
            raise TypeError("forward_fn and reverse_fn must be callable functions.")
        self._forward_fn = forward_fn
        self._reverse_fn = reverse_fn
        self._name = name

    @property
    def name(self) -> str:
        """Returns operator descriptor name."""
        return self._name

    def apply_basis(self, basis: QuantumBasisState) -> QuantumBasisState:
        """
        Computes forward basis state transition U_P |C_R⟩ = |R_P(C_R)⟩.

        Implements central correspondence theorem: (U_P ∘ ι)(C_R) = (ι ∘ R_P)(C_R).

        :param basis: Basis state |C_R⟩.
        :return: Target basis state |R_P(C_R)⟩.
        """
        if not isinstance(basis, QuantumBasisState):
            raise TypeError("apply_basis requires a QuantumBasisState argument.")
        next_config = self._forward_fn(basis.config)
        return iota(next_config)

    def apply_basis_adjoint(self, basis: QuantumBasisState) -> QuantumBasisState:
        """
        Computes inverse/adjoint basis state transition U_P† |C_R'⟩ = |R_P^{-1}(C_R')⟩.

        Implements inverse correspondence theorem: (U_P† ∘ ι)(C_R') = (ι ∘ R_P^{-1})(C_R').

        :param basis: Basis state |C_R'⟩.
        :return: Predecessor basis state |R_P^{-1}(C_R')⟩.
        """
        if not isinstance(basis, QuantumBasisState):
            raise TypeError("apply_basis_adjoint requires a QuantumBasisState argument.")
        prev_config = self._reverse_fn(basis.config)
        return iota(prev_config)

    def apply_state(self, state: QTMStateVector) -> QTMStateVector:
        """
        Computes linear extension of U_P over superposition state vector:
        U_P Σ α_C |C_R⟩ = Σ α_C |R_P(C_R)⟩.

        :param state: QTMStateVector |ψ⟩.
        :return: Evolved QTMStateVector U_P |ψ⟩.
        """
        if not isinstance(state, QTMStateVector):
            raise TypeError("apply_state requires a QTMStateVector argument.")

        evolved_amps: Dict[QuantumBasisState, complex] = {}
        for basis, amp in state.amplitudes.items():
            target_basis = self.apply_basis(basis)
            evolved_amps[target_basis] = evolved_amps.get(target_basis, 0.0 + 0.0j) + amp

        return QTMStateVector(evolved_amps)

    def apply_state_adjoint(self, state: QTMStateVector) -> QTMStateVector:
        """
        Computes linear extension of U_P† over superposition state vector:
        U_P† Σ α_C |C_R'⟩ = Σ α_C |R_P^{-1}(C_R')⟩.

        :param state: QTMStateVector |ψ⟩.
        :return: Evolved QTMStateVector U_P† |ψ⟩.
        """
        if not isinstance(state, QTMStateVector):
            raise TypeError("apply_state_adjoint requires a QTMStateVector argument.")

        evolved_amps: Dict[QuantumBasisState, complex] = {}
        for basis, amp in state.amplitudes.items():
            source_basis = self.apply_basis_adjoint(basis)
            evolved_amps[source_basis] = evolved_amps.get(source_basis, 0.0 + 0.0j) + amp

        return QTMStateVector(evolved_amps)

    def adjoint(self) -> "LiftedUnitaryOperator":
        """
        Returns the Hermitian adjoint operator U_P†.

        Swaps forward_fn and reverse_fn.
        """
        adjoint_name = f"{self._name}†" if not self._name.endswith("†") else self._name[:-1]
        return LiftedUnitaryOperator(
            forward_fn=self._reverse_fn,
            reverse_fn=self._forward_fn,
            name=adjoint_name,
        )

    def verify_bijectivity(
        self, domain: Set[QuantumBasisState]
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies that transition function R_P is total and bijective over finite transition-closed domain.

        Enforces requirements:
        1. Domain closure: R_P(domain) ⊆ domain.
        2. Bijectivity: Image size equals domain size (no collisions).
        3. Round-trip consistency: R_P^{-1}(R_P(C)) == C for all C in domain.

        :param domain: Finite set of QuantumBasisState objects.
        :return: Tuple (is_bijective, error_message).
        """
        if not domain:
            return True, None

        image_set: Set[QuantumBasisState] = set()
        for basis in domain:
            target = self.apply_basis(basis)
            if target not in domain:
                return False, f"Transition closure failure: U_P({basis}) = {target} not in domain."

            if target in image_set:
                return False, f"Injectivity collision failure: Duplicate image target {target} detected."
            image_set.add(target)

            # Inverse round trip test
            reverse_target = self.apply_basis_adjoint(target)
            if reverse_target != basis:
                return False, f"Round-trip failure: U_P†(U_P({basis})) = {reverse_target} != {basis}."

        if len(image_set) != len(domain):
            return False, f"Surjectivity failure: Image size ({len(image_set)}) != domain size ({len(domain)})."

        return True, None

    def verify_unitarity(
        self, domain: Set[QuantumBasisState], tol: float = DEFAULT_TOLERANCE
    ) -> Tuple[bool, Optional[str]]:
        """
        Executable verification of unitarity U_P† U_P = I and U_P U_P† = I over a finite transition-closed domain.

        Also verifies norm preservation and inner-product preservation across basis states.

        :param domain: Finite set of basis states.
        :param tol: Numerical verification tolerance.
        :return: Tuple (is_unitary, error_message).
        """
        is_bij, bij_err = self.verify_bijectivity(domain)
        if not is_bij:
            return False, f"Unitarity verification failed due to bijectivity violation: {bij_err}"

        # Test state vector round trips & norm preservation
        basis_list = list(domain)
        for b in basis_list:
            v_b = QTMStateVector({b: 1.0 + 0.0j})
            v_forward = self.apply_state(v_b)
            v_round_trip = self.apply_state_adjoint(v_forward)

            if abs(v_forward.norm() - 1.0) > tol:
                return False, f"Norm preservation failure for {b}: ||U_P b|| = {v_forward.norm()} != 1.0."

            if v_round_trip != v_b:
                return False, f"Round-trip unitarity failure: U_P† U_P |{b}⟩ != |{b}⟩."

        return True, None

    def get_permutation_matrix(
        self, domain_list: List[QuantumBasisState]
    ) -> PermutationMatrixRepresentation:
        """
        Constructs finite N x N permutation matrix [U_P] over ordered basis domain_list.

        :param domain_list: Ordered list of QuantumBasisState objects.
        :return: PermutationMatrixRepresentation instance.
        """
        N = len(domain_list)
        basis_map = {b: idx for idx, b in enumerate(domain_list)}
        matrix = [[0.0 + 0.0j for _ in range(N)] for _ in range(N)]

        for col_j, b_j in enumerate(domain_list):
            b_target = self.apply_basis(b_j)
            if b_target not in basis_map:
                raise ValueError(f"Domain list is not transition-closed: U_P({b_j}) = {b_target} not in domain_list.")
            row_i = basis_map[b_target]
            matrix[row_i][col_j] = 1.0 + 0.0j

        return PermutationMatrixRepresentation(domain_list, matrix)


def create_unitary_operator_from_program(program: UTMProgram) -> LiftedUnitaryOperator:
    """
    Constructs a LiftedUnitaryOperator U_P from a Module 1 UTMProgram,
    using Module 2 forward_step_rutm and reverse_step_rutm semantics.

    :param program: Frozen Module 1 UTMProgram instance.
    :return: LiftedUnitaryOperator instance.
    """
    if not isinstance(program, UTMProgram):
        raise TypeError("program must be a valid UTMProgram instance.")

    def forward_fn(config: RUTMConfiguration) -> RUTMConfiguration:
        return forward_step_rutm(config, program)

    def reverse_fn(config: RUTMConfiguration) -> RUTMConfiguration:
        return reverse_step_rutm(config, program)

    return LiftedUnitaryOperator(
        forward_fn=forward_fn,
        reverse_fn=reverse_fn,
        name=f"U_P[{program.name if hasattr(program, 'name') else 'UTMProgram'}]",
    )


def create_unitary_operator_from_mapping(
    mapping: Dict[QuantumBasisState, QuantumBasisState]
) -> LiftedUnitaryOperator:
    """
    Constructs a LiftedUnitaryOperator from an explicit finite basis state mapping {|C_i⟩ -> |C_j⟩}.

    Validates total bijectivity over domain D immediately. For configurations outside D,
    forward_fn and reverse_fn perform an explicit identity extension R_P(C) = C over C_R \\ D,
    maintaining total global bijectivity across all of C_R.

    :param mapping: Dictionary mapping QuantumBasisState -> QuantumBasisState.
    :return: LiftedUnitaryOperator instance.
    :raises ValueError: If mapping is non-bijective, empty, or not transition-closed.
    """
    if not mapping:
        raise ValueError("Cannot create unitary operator from empty mapping.")

    domain = set(mapping.keys())
    image = set(mapping.values())

    # Bijectivity checks
    if len(domain) != len(image):
        raise ValueError(
            f"Non-bijective mapping: Domain size ({len(domain)}) != Image size ({len(image)}). "
            "Collisions prevent unitary operator construction."
        )

    if domain != image:
        raise ValueError(
            "Mapping is not transition-closed over domain (Domain != Image). "
            "Cannot induce a valid square unitary matrix."
        )

    # Construct inverse dictionary
    inverse_mapping = {target: source for source, target in mapping.items()}

    def forward_fn(config: RUTMConfiguration) -> RUTMConfiguration:
        b = iota(config)
        if b not in mapping:
            # Identity extension R_P(C) = C over complementary domain C_R \ D
            return config
        return mapping[b].config

    def reverse_fn(config: RUTMConfiguration) -> RUTMConfiguration:
        b = iota(config)
        if b not in inverse_mapping:
            # Identity extension R_P^{-1}(C) = C over complementary domain C_R \ D
            return config
        return inverse_mapping[b].config

    return LiftedUnitaryOperator(
        forward_fn=forward_fn,
        reverse_fn=reverse_fn,
        name="U_P[ExplicitMapping]",
    )
