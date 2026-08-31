# Module 6 Stage 3 Specification — Compiler Mapping F Formulation & Domain/Codomain Bounds

**Module:** Module 6 — Classical-to-Quantum Expressibility & Equivalence Analysis  
**Stage:** Stage 3 — Compiler Mapping F Formulation & Domain/Codomain Bounds  
**Status:** FORMALLY COMPLETE / FROZEN  

---

## 1. Mathematical Definitions & Summary

1. **Definition 1 (Domain $A_C$):**  
   $A_C = A_\text{semantic}$ is the set of classical algorithms represented by finite, deterministic, semantically valid transition systems $(D_\text{fin}, R_P)$ derived from Module 1 / Module 2 UTM & RUTM programs.  
   *Classification: DEFINITION.*

2. **Definition 2 (Logical Codomain $C_Q^\text{logical}$):**  
   $C_Q^\text{logical}$ is the set of valid logical `QuantumCircuitIR` AST objects admitted by the frozen Module 4 contract.  
   *Classification: DEFINITION.*

3. **Definition 3 (Semantic Quotient Codomain $C_Q^\text{semantic}$):**  
   $C_Q^\text{semantic} = C_Q^\text{logical} / \equiv_Q$ is the space of logical quantum circuits quotiented by operator equivalence $\equiv_Q$.  
   *Classification: DEFINITION.*

4. **Definition 4 (Compiler Mapping $F$):**  
   $F : A_C \to C_Q^\text{logical}$ is the compositional mapping induced by the frozen Module 1 $\to$ 2 $\to$ 3 $\to$ 4 compiler synthesis pipeline ($\text{AML/RUTM} \to \text{RUTM-IR} \to \text{QTM-IR} \to \text{QuantumCircuitIR}$).  
   *Classification: DEFINITION / CONTRACT.*

5. **Definition 5 (Structural Image $\text{Img}(F)$):**  
   $\text{Img}(F) = \{ F(A) \mid A \in A_C \} \subseteq C_Q^\text{reversible} \subseteq C_Q^\text{logical}$.  
   *Classification: FORMAL THEOREM.*

6. **Definition 6 (Semantic Image $\text{Img}_Q(F)$):**  
   $\text{Img}_Q(F) = \{ [F(A)]_Q \mid A \in A_C \} \subseteq \text{Perm}(2^N) \subset M_{2^N}(\mathbb{R}) \subset \text{U}(2^N)$.  
   *Classification: FORMAL THEOREM.*

7. **Definition 7 (Quotient Mapping $\bar{F}$):**  
   $\bar{F} : A_C / \equiv_C \to C_Q^\text{logical} / \equiv_Q$ is well-defined under condition $A_1 \equiv_C A_2 \implies F(A_1) \equiv_Q F(A_2)$, verified as `WELL_DEFINED_OBSERVED`.  
   *Classification: EXECUTABLE VERIFICATION.*

8. **Definition 8 (Empirical Restriction $F_N$):**  
   $F_N : A_N \to C_Q^\text{logical}$ maps finite sample family $A_N \subset A_C$ to empirical image $\text{Img}_N(F)$.  
   *Classification: EMPIRICAL OBSERVATION.*

9. **Definition 9 (Operator Class $\text{Perm}(2^N)$):**  
   All compiler-generated unitaries $U_F(A)$ belong to the computational-basis binary permutation group $\text{Perm}(2^N)$.  
   *Classification: FORMAL THEOREM.*

10. **Definition 10 (Hadamard Formal Exclusion Theorem):**  
    Every compiler unitary $U_F(A) \in \text{Perm}(2^N)$. Hadamard gate $H = \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix} \notin \text{Perm}(2)$ due to non-binary matrix entries. Therefore, $H \notin \text{Img}_Q(F)$.  
    *Classification: FORMAL THEOREM.*

---

## 2. Claim-vs-Executable Evidence Matrix

| Statement | Classification | Evidence / Basis | Verification Status |
|---|---|---|---|
| Domain $A_C$ Formally Defined | **DEFINITION** | $(D_\text{fin}, R_P)$ derived from Module 1/2 contracts | **VERIFIED** |
| Codomain $C_Q^\text{logical}$ Formally Defined | **DEFINITION** | Module 4 `QuantumCircuitIR` AST space | **VERIFIED** |
| Compiler Mapping $F$ Formally Defined | **CONTRACT** | Compositional Module 1 $\to$ 4 compiler pipeline | **VERIFIED** |
| Mapping Totality | **THEOREM** | `TOTAL_OVER_DEFINED_DOMAIN` for valid $A \in A_C$ | **VERIFIED** |
| Quotient Well-Definedness | **VERIFICATION** | `WELL_DEFINED_OBSERVED` ($A_1 \equiv_C A_2 \implies F(A_1) \equiv_Q F(A_2)$) | **VERIFIED** |
| Structural Image Bound | **THEOREM** | $\text{Img}(F) \subseteq C_Q^\text{reversible} \subseteq C_Q^\text{logical}$ | **VERIFIED** |
| Semantic Image Bound | **THEOREM** | $\text{Img}_Q(F) \subseteq \text{Perm}(2^N) \subset M_{2^N}(\mathbb{R}) \subset \text{U}(2^N)$ | **VERIFIED** |
| Computational-Basis Permutation Invariant | **THEOREM** | All primitive gates $\{X, \text{CNOT}, \text{TOFFOLI}\}$ preserve basis bitstrings | **VERIFIED** |
| Real Amplitude Invariant | **THEOREM** | Matrix entries of $U_F(A)$ are purely real numbers | **VERIFIED** |
| Superposition Capability | **THEOREM** | `PROVEN_NOT_GENERATING` (0 superposition generated on basis states) | **VERIFIED** |
| Composition & Inverse Closure | **THEOREM** | Permutation group $\text{Perm}(2^N)$ is closed under matrix multiplication & transpose | **VERIFIED** |
| Hadamard Formal Exclusion | **THEOREM** | $H \notin \text{Perm}(2) \implies H \notin \text{Img}_Q(F)$ (`FORMALLY_EXCLUDED`) | **VERIFIED** |
| $F$ Injectivity | **UNPROVEN** | Empirically reported as `NO_COLLISION_OBSERVED` | **UNPROVEN** |
| $F$ Surjectivity | **UNPROVEN** | Universal surjectivity over $\text{U}(2^N)$ remains `UNPROVEN` | **UNPROVEN** |
| Universal Expressibility | **UNPROVEN** | Universal expressibility over $\text{U}(2^N)$ remains `UNPROVEN` | **UNPROVEN** |

---

## 3. Implementation Structure

1. **`src/module6/mapping/`**:
   - `identity.py`: `ClassicalAlgorithmIdentity`, `create_classical_algorithm_identity`.
   - `model.py`: `DomainDescriptor`, `CodomainDescriptor`, `CompilerMappingRecord`, `SemanticQuotientRecord`, `MappingComplexityRecord`.
   - `quotient.py`: `QuotientWellDefinednessAnalyzer`.
2. **`src/module6/bounds/`**:
   - `cardinality.py`: `CardinalityBound`, `CardinalityType`.
   - `domain.py`: `DomainBoundsAnalyzer`.
   - `codomain.py`: `CodomainBoundsAnalyzer`.
   - `image.py`: `ImageBound`, `ImageBoundsAnalyzer`.
   - `operator_class.py`: `OperatorClassDescriptor`.
3. **`src/module6/invariants/`**:
   - `permutation.py`: `PermutationInvariantAnalyzer`.
   - `amplitude.py`: `RealAmplitudeInvariantAnalyzer`.
   - `composition.py`: `SuperpositionCapabilityAnalyzer`, `CompositionClosureAnalyzer`, `InverseClosureAnalyzer`, `IdentityElementAnalyzer`.
   - `analyzer.py`: `StructuralInvariantAnalyzer`, `StructuralInvariantResult`.
4. **`src/module6/analysis/`**:
   - `stage3.py`: `analyze_compiler_mapping_stage3`.
   - `report.py`: `Stage3AnalysisReport`, `serialize_stage3_report`, `deserialize_stage3_report`.
