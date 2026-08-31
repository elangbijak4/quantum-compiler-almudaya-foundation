# Module 6 Stage 7 — Formal Terminology & Ontology

## 1. Terminology Definitions

- **Evolutionary State ($GE(k)$)**: The persistent, cumulative gate vocabulary achieved by the compiler at evolutionary stage $k$.
- **Session Baseline ($B_u$)**: A temporary, user-selected subset configuration $B_u \subseteq GE(k)$ active for the current compilation session.
- **Effective Vocabulary ($G_{\text{effective}}$)**: The resolved gate vocabulary actually permitted during compilation ($B_u$ or $GE(k)$).
- **Effective Compilation Context**: The immutable object carrying effective vocabulary, policies, status, conflicts, and provenance passed into compilation analysis.
- **Resolution Function ($R$)**: The formal function mapping evolutionary state, session baseline, and constraints to `EffectiveCompilationContext`.
- **Governed Promotion**: The formal process requiring explicit authorization before candidate gates enter production $GE(k)$.
- **Three-Level Diagnosis**: The diagnostic hierarchy distinguishing Level 1 (User baseline insufficient), Level 2 (Evolutionary baseline insufficient), and Level 3 (Inconclusive).
