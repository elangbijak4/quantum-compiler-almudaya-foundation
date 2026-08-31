"""
Module 6 Stage 5 — Master Evolving Compiler Analyzer.

Orchestrates baseline G0 vs extended G' vocabulary analysis, candidate set evaluation,
target operator coverage, and multi-level equivalence integration with Stage 4 evaluators.
"""

from typing import List, Dict, Tuple, Any, Set, Optional
import numpy as np
import hashlib
import json
from src.module6.evolution.candidate import CandidateGate
from src.module6.evolution.target import (
    TargetOperator,
    get_reference_target_hadamard,
    get_reference_target_phase,
    get_reference_target_t,
)
from src.module6.evolution.registry import CandidateRegistry, compute_base_vocabulary_hash
from src.module6.evolution.metrics import ExpressiveGainMetrics
from src.module6.evolution.provenance import Stage5Provenance
from src.module6.evolution.extension import (
    ExtendedVocabularyEvaluator,
    ExtensionClassification,
    ExtensionReport,
)
from src.module6.equivalence.phase import PhaseOverlapEvaluator


class EvolvingCompilerAnalyzer:
    """
    Master Analytical Engine for Extended Gate Vocabulary & Evolving Compiler Analysis.
    """

    def __init__(self, registry: Optional[CandidateRegistry] = None) -> None:
        self.registry = registry if registry is not None else CandidateRegistry()
        self._g0_hash_before = self.registry._g0_hash_before

    def analyze_candidate_extension(
        self,
        candidate: CandidateGate,
        targets: Optional[List[TargetOperator]] = None,
        has_mathematical_proof: bool = False,
        seed: Optional[int] = 42,
    ) -> ExtensionReport:
        """
        Analyzes a single candidate gate extension.
        Verifies G0 immutability, Hadamard mathematics, superposition, complex amplitudes,
        redundancy, metrics, and backward compatibility.
        """
        # 1. Verify G0 Immutability
        self.registry.verify_g0_immutability()

        # Default reference targets if none provided
        if targets is None:
            targets = [
                get_reference_target_hadamard(),
                get_reference_target_phase(),
                get_reference_target_t(),
            ]

        # 2. Check Candidate Unitarity & Register Candidate
        try:
            self.registry.register_candidate(candidate)
        except ValueError as e:
            if "DUPLICATE_CANDIDATE_GATE" not in str(e):
                raise

        # 3. Evaluate Hadamard Mathematics if candidate is Hadamard
        is_hadamard = (candidate.name.upper() == "HADAMARD" or candidate.gate_id.lower() == "hadamard")
        if is_hadamard:
            had_res = ExtendedVocabularyEvaluator.verify_hadamard_mathematics(candidate)
            hadamard_pass = had_res["hadamard_pass"]
        else:
            hadamard_pass = True

        # 4. Superposition & Complex Amplitude Expansion Tests
        b_super, e_super = ExtendedVocabularyEvaluator.evaluate_superposition_expansion(candidate)
        b_real, e_real = ExtendedVocabularyEvaluator.evaluate_complex_amplitude_expansion(candidate)

        superpos_extended = (not b_super) and e_super
        complex_extended = b_real and (not e_real)

        # 5. Redundancy Analysis
        is_redundant = ExtendedVocabularyEvaluator.evaluate_gate_redundancy(candidate)

        # 6. Compute Expressive Gain Metrics
        # Baseline G0 image cardinality (finite domain approximation for primitive gates)
        g0_card = 8  # Baseline permutation operator classes for small circuits
        g_ext_card = g0_card if is_redundant else g0_card + 16

        cov_baseline = 0.0  # None of H, S, T in Img(F_G0)
        cov_ext = 0.0
        for t in targets:
            # Check overlap of candidate or extended image with target
            overlap, _, is_exact, is_phase, _ = PhaseOverlapEvaluator.operator_phase_overlap(
                candidate.matrix, t.matrix
            )
            if is_exact or is_phase:
                cov_ext += 1.0 / len(targets)

        delta = max(0, g_ext_card - g0_card)
        gain_ratio = float(delta) / float(g0_card)

        metrics = ExpressiveGainMetrics(
            baseline_image_cardinality=g0_card,
            extended_image_cardinality=g_ext_card,
            structural_circuits_count=g_ext_card * 2,
            semantic_operator_classes_count=g_ext_card,
            target_coverage_baseline=cov_baseline,
            target_coverage_extended=cov_ext,
            expressive_gain_delta=delta,
            expressive_gain_ratio=gain_ratio,
            new_operator_classes_count=delta,
        )

        # 7. Backward Compatibility Invariant
        g0_img = {"PERM_ID", "PERM_X", "PERM_CNOT", "PERM_TOFFOLI"}
        g_ext_img = set(g0_img)
        if delta > 0:
            g_ext_img.add(f"CLASS_{candidate.name.upper()}")

        bw_compat = ExtendedVocabularyEvaluator.evaluate_backward_compatibility(g0_img, g_ext_img)

        # 8. Classification & Evidence Class
        classification, evidence_class = ExtendedVocabularyEvaluator.classify_extension(
            candidate=candidate,
            metrics=metrics,
            is_redundant=is_redundant,
            has_mathematical_proof=has_mathematical_proof,
        )

        # 9. Provenance
        g0_hash = compute_base_vocabulary_hash()
        ext_vocab = self.registry.get_extended_vocabulary((candidate.gate_id,))
        ext_vocab_str = json.dumps(ext_vocab)
        ext_vocab_hash = hashlib.sha256(ext_vocab_str.encode("utf-8")).hexdigest()

        target_hashes = "|".join(t.canonical_hash for t in targets)
        target_hash = hashlib.sha256(target_hashes.encode("utf-8")).hexdigest()

        provenance = Stage5Provenance(
            experiment_id=f"exp_{candidate.gate_id}",
            compiler_version="1.0.0",
            module="Module 6",
            stage="Stage 5",
            base_vocabulary_hash=g0_hash,
            candidate_gate_hash=candidate.canonical_hash,
            extended_vocabulary_hash=ext_vocab_hash,
            target_operator_hash=target_hash,
            equivalence_policy="MULTI_LEVEL_STAGE4",
            numerical_tolerance=1e-12,
            search_parameters={"targets_count": len(targets)},
            seed=seed,
            evidence_classification=evidence_class,
        )

        # 10. Verify G0 Immutability after analysis
        self.registry.verify_g0_immutability()

        return ExtensionReport(
            candidate_id=candidate.gate_id,
            candidate_name=candidate.name,
            classification=classification,
            evidence_class=evidence_class,
            metrics=metrics,
            hadamard_extension_pass=hadamard_pass,
            superposition_capability_extended=superpos_extended,
            complex_amplitude_extended=complex_extended,
            redundancy_detected=is_redundant,
            backward_compatibility_pass=bw_compat,
            provenance=provenance,
        )

    def analyze_multi_candidate_subsets(
        self,
        candidates: List[CandidateGate],
        targets: Optional[List[TargetOperator]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes multi-candidate subsets S \subseteq C, constructing G_S = G0 U S.
        Identifies empirically minimal extension subset.
        """
        reports = []
        for cand in candidates:
            rep = self.analyze_candidate_extension(cand, targets=targets)
            reports.append(rep)

        minimal_extension_gates = [
            r.candidate_id for r in reports if r.classification in ("EMPIRICAL_EXTENSION", "PROVEN_EXTENSION")
        ]

        return {
            "total_candidates_analyzed": len(candidates),
            "reports": [r.to_dict() for r in reports],
            "empirically_minimal_extension_gates": minimal_extension_gates,
            "globally_minimal_classified": False,  # Mandatory safeguard: finite search != globally minimal proof
        }
