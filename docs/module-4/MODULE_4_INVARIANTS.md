# Module 4 Invariants & Formal Constraints

**Module:** Module 4 — Quantum Circuit Synthesis  
**Status:** SCOPE REVIEW & MICRO CLOSURE COMPLETE / FROZEN INVARIANTS  

---

## 1. Constitutional Invariants

Module 4 enforces seven strict mathematical and architectural invariants:

1. **Restricted-Domain Semantic Preservation (`CONFIRMED`):**  
   The synthesized circuit unitary $U_C$ must preserve the transition operator $R_P$ on all $C \in D_\text{fin}$:
   $$U_C |E(C)\rangle = |E(R_P(C))\rangle$$

2. **Register Encoding Injectivity (`CONFIRMED`):**  
   The configuration encoding $E : D_\text{fin} \to \{0,1\}^n$ must be strictly injective:
   $$C_1 \neq C_2 \implies E(C_1) \neq E(C_2)$$

3. **Domain Transition Closure (`CONFIRMED`):**  
   $D_\text{fin}$ must be closed under $R_P$ ($R_P(D_\text{fin}) \subseteq D_\text{fin}$) and $R_P^{-1}$ ($R_P^{-1}(D_\text{fin}) \subseteq D_\text{fin}$) for the declared step horizon $T$.

4. **Logical History Integrity (`CONFIRMED`):**  
   Classical history $H$ must be encoded into configuration registers when non-empty, and cannot be equated to physical ancillas.

5. **Clean Ancilla Uncomputation (`CONFIRMED`):**  
   All physical workspace ancillas allocated during synthesis must undergo Bennett uncomputation back to $|0\rangle$ at circuit termination.

6. **3-Level Equivalence Verification Policy (`CONFIRMED`):**  
   Circuit equivalence enforces exact symbolic basis matching, numerical state vector norm comparison ($\epsilon < 10^{-12}$), and matrix operator norm comparison ($\epsilon < 10^{-12}$).

7. **Compiler Provenance & Determinism (`CONFIRMED`):**  
   Synthesized circuits must preserve complete provenance metadata and synthesize 100% deterministically.
