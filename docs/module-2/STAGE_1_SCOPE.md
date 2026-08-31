# Stage 1 Scope — RUTM Specification

This file is intentionally a scope marker for the first authorized
stage. The implementation agent must replace/expand this artifact during
Stage 1 with the actual formal RUTM specification.

Stage 1 must answer, with mathematical precision:

1. What is a RUTM in this project?
2. What is its configuration tuple?
3. What is its forward transition function?
4. What is its inverse transition function?
5. On what domain is the transition reversible?
6. What information is stored in auxiliary/history state?
7. What constitutes configuration equality?
8. How are blank symbols handled?
9. How are head movements reversed?
10. How are state transitions reversed?
11. How is HALT represented?
12. What invariant is maintained by the history encoding?
13. What theorem/proof obligation establishes reversibility?
14. What does the model explicitly NOT claim about thermodynamic
    reversibility?

Do not implement Stage 2 or later while Stage 1 is unresolved.
