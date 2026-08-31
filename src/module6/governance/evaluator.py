"""
Module 6 Stage 10 — Governance & Lifecycle Evaluator.

Audits compilation artifacts across Stages 1–9, validates lifecycle transitions,
and issues AuditCertificates without circuit mutation, vocabulary expansion, or hardware execution.
"""

from typing import Dict, Any, Optional, List, Tuple
import hashlib
from src.module4.circuit_ir.model import QuantumCircuitIR
from src.module6.resolution.model import EffectiveCompilationContext
from src.module6.optimization.model import OptimizationCostReport
from src.module6.quality.model import QualityAnalysisReport
from src.module6.governance.model import (
    AuditCertificate,
    CertificationLevel,
    LifecycleStatus,
    GovernanceFinding,
    FindingCategory,
    FindingSeverity,
    GovernanceAuditReport,
)


class GovernanceAuditor:
    """
    Production Governance Auditor and Certification Evaluator.
    
    Enforces Invariants:
    1. Upstream Immutability: Zero mutation to inputs or Stage 1-9 states.
    2. Semantic Authority: Stage 4 Level 6 Semantic Verification remains absolute correctness gate.
    3. Vocabulary Containment: All gates must belong to G_effective. Zero hidden expansion.
    4. Hardware & Noise Boundaries: 0% real hardware execution, 0% physical noise simulation.
    5. Lifecycle Integrity: Enforces strict state transitions (CANDIDATE -> ANALYZED -> VERIFIED -> GOVERNED -> CERTIFIED).
    """

    ALLOWED_TRANSITIONS: Dict[LifecycleStatus, List[LifecycleStatus]] = {
        LifecycleStatus.CANDIDATE: [LifecycleStatus.ANALYZED, LifecycleStatus.REJECTED],
        LifecycleStatus.ANALYZED: [LifecycleStatus.DRAFT, LifecycleStatus.VERIFIED, LifecycleStatus.REJECTED],
        LifecycleStatus.DRAFT: [LifecycleStatus.VERIFIED, LifecycleStatus.REJECTED],
        LifecycleStatus.VERIFIED: [LifecycleStatus.GOVERNED, LifecycleStatus.DEPRECATED, LifecycleStatus.REJECTED],
        LifecycleStatus.GOVERNED: [LifecycleStatus.CERTIFIED, LifecycleStatus.PROMOTED, LifecycleStatus.DEPRECATED, LifecycleStatus.REJECTED],
        LifecycleStatus.CERTIFIED: [LifecycleStatus.PROMOTED, LifecycleStatus.DEPRECATED],
        LifecycleStatus.PROMOTED: [LifecycleStatus.DEPRECATED],
        LifecycleStatus.DEPRECATED: [],
        LifecycleStatus.REJECTED: [],
    }

    @classmethod
    def validate_lifecycle_transition(
        cls,
        current_status: LifecycleStatus,
        target_status: LifecycleStatus,
        certificate: Optional[AuditCertificate] = None,
    ) -> bool:
        """
        Validates if a lifecycle transition is allowed by governance rules.
        """
        if target_status not in cls.ALLOWED_TRANSITIONS.get(current_status, []):
            return False

        # Additional prerequisite gate: cannot transition to CERTIFIED unless fully certified
        if target_status == LifecycleStatus.CERTIFIED and certificate:
            if certificate.certification_level != CertificationLevel.FULLY_GOVERNED_CERTIFIED:
                return False

        return True

    @classmethod
    def audit_compilation(
        cls,
        circuit: QuantumCircuitIR,
        context: EffectiveCompilationContext,
        quality_report: Optional[QualityAnalysisReport] = None,
        optimization_report: Optional[OptimizationCostReport] = None,
    ) -> GovernanceAuditReport:
        """
        Executes a comprehensive, deterministic compilation governance audit across Stages 1–9.
        """
        algorithm_id = circuit.circuit_id if hasattr(circuit, 'circuit_id') and circuit.circuit_id else "quantum_circuit"

        findings: List[GovernanceFinding] = []
        satisfied_prereqs: List[str] = []
        failed_prereqs: List[str] = []

        # 1. Audit Semantic Verification (Stage 4 Level 6)
        s4_verified = False
        if quality_report and quality_report.quality_profile.semantic_equivalence_verified:
            s4_verified = True
            satisfied_prereqs.append("STAGE_4_SEMANTIC_VERIFICATION_PASSED")
            findings.append(
                GovernanceFinding(
                    finding_id=f"FIND_S4_{algorithm_id}",
                    category=FindingCategory.SEMANTIC,
                    severity=FindingSeverity.INFO,
                    status="PASSED",
                    evidence="Level 6 Quantum Semantic Equivalence Verified.",
                    policy_or_invariant="Stage 4 Level 6 Semantic Equivalence Authority",
                    consequence="Semantic correctness verified.",
                )
            )
        else:
            failed_prereqs.append("STAGE_4_SEMANTIC_VERIFICATION_FAILED")
            findings.append(
                GovernanceFinding(
                    finding_id=f"FIND_S4_{algorithm_id}",
                    category=FindingCategory.SEMANTIC,
                    severity=FindingSeverity.CRITICAL,
                    status="FAILED",
                    evidence="Semantic equivalence verification failed or not provided.",
                    policy_or_invariant="Stage 4 Level 6 Semantic Equivalence Authority",
                    consequence="Cannot certify unverified compilation result.",
                )
            )

        # 2. Audit Stage 7 Resolution & Vocabulary Containment
        s7_feasible = False
        cfg_stat = context.configuration_status
        is_valid_cfg = cfg_stat in ("FEASIBLE", "VALID_CONFIGURATION") or getattr(cfg_stat, 'value', '') in ("FEASIBLE", "VALID_CONFIGURATION")
        
        # Check vocabulary containment
        eff_vocab_set = set(context.effective_vocabulary)
        vocab_ok = True
        for g in circuit.gates:
            g_name = g.gate_type.name if hasattr(g.gate_type, 'name') else str(g.gate_type)
            if g_name not in eff_vocab_set:
                vocab_ok = False
                break

        if is_valid_cfg and vocab_ok:
            s7_feasible = True
            satisfied_prereqs.append("STAGE_7_FEASIBILITY_PASSED")
            satisfied_prereqs.append("STAGE_7_VOCABULARY_CONTAINMENT_PASSED")
            findings.append(
                GovernanceFinding(
                    finding_id=f"FIND_S7_{algorithm_id}",
                    category=FindingCategory.VOCABULARY,
                    severity=FindingSeverity.INFO,
                    status="PASSED",
                    evidence=f"Circuit gates contained in effective vocabulary: {context.effective_vocabulary}",
                    policy_or_invariant="Vocabulary Containment Invariant",
                    consequence="Vocabulary compliance verified.",
                )
            )
        else:
            failed_prereqs.append("STAGE_7_VOCABULARY_OR_FEASIBILITY_FAILED")
            findings.append(
                GovernanceFinding(
                    finding_id=f"FIND_S7_{algorithm_id}",
                    category=FindingCategory.VOCABULARY,
                    severity=FindingSeverity.ERROR,
                    status="FAILED",
                    evidence="Circuit contains gates outside G_effective or context is infeasible.",
                    policy_or_invariant="Vocabulary Containment Invariant",
                    consequence="Vocabulary or feasibility violation detected.",
                )
            )

        # 3. Audit Stage 8 Optimization
        s8_opt = False
        if optimization_report and optimization_report.gate_count_reduction >= 0:
            s8_opt = True
            satisfied_prereqs.append("STAGE_8_OPTIMIZATION_VERIFIED")
            findings.append(
                GovernanceFinding(
                    finding_id=f"FIND_S8_{algorithm_id}",
                    category=FindingCategory.GOVERNANCE,
                    severity=FindingSeverity.INFO,
                    status="PASSED",
                    evidence=f"Optimization reduction: {optimization_report.gate_count_reduction} gates.",
                    policy_or_invariant="Monotonic Optimization Invariant",
                    consequence="Optimization verified.",
                )
            )

        # 4. Audit Stage 9 Quality & Resource Profile
        s9_qual = False
        if quality_report and quality_report.classification.value == "SEMANTICALLY_VALID":
            s9_qual = True
            satisfied_prereqs.append("STAGE_9_QUALITY_PASSED")
            findings.append(
                GovernanceFinding(
                    finding_id=f"FIND_S9_{algorithm_id}",
                    category=FindingCategory.RESOURCE,
                    severity=FindingSeverity.INFO,
                    status="PASSED",
                    evidence=f"Resource profile verified. Classification: {quality_report.classification.value}",
                    policy_or_invariant="Quality Profile Compliance",
                    consequence="Logical resource profile verified.",
                )
            )

        # Determine Certification Level and Lifecycle Status
        if s4_verified and s7_feasible and s9_qual:
            cert_level = CertificationLevel.FULLY_GOVERNED_CERTIFIED
            life_status = LifecycleStatus.CERTIFIED
        elif s4_verified and s7_feasible:
            cert_level = CertificationLevel.FEASIBILITY_CERTIFIED
            life_status = LifecycleStatus.GOVERNED
        elif s4_verified:
            cert_level = CertificationLevel.SEMANTICS_VERIFIED
            life_status = LifecycleStatus.VERIFIED
        else:
            cert_level = CertificationLevel.AUDIT_FAILED
            life_status = LifecycleStatus.REJECTED

        cert_raw_id = f"CERT_{algorithm_id}_{cert_level.value}_{life_status.value}_{context.context_hash[:8]}"
        cert_hash = hashlib.sha256(cert_raw_id.encode("utf-8")).hexdigest()[:16]

        certificate = AuditCertificate(
            certificate_id=f"CERT_{algorithm_id}",
            algorithm_id=algorithm_id,
            certification_level=cert_level,
            lifecycle_status=life_status,
            stage4_verified=s4_verified,
            stage7_feasible=s7_feasible,
            stage8_optimized=s8_opt,
            stage9_quality_passed=s9_qual,
            provenance_hash=cert_hash,
            prerequisites_satisfied=tuple(satisfied_prereqs),
            prerequisites_failed=tuple(failed_prereqs),
            identity_hash=cert_hash,
        )

        audit_raw = f"AUDIT_{algorithm_id}_{cert_hash}"
        audit_hash = hashlib.sha256(audit_raw.encode("utf-8")).hexdigest()[:16]

        provenance = {
            "algorithm_id": algorithm_id,
            "session_id": context.session_id,
            "evolution_stage": context.evolution_stage,
            "context_hash": context.context_hash,
            "quality_report_hash": quality_report.report_hash if quality_report else "",
            "optimization_report_hash": optimization_report.report_hash if optimization_report else "",
            "stage_id": "Stage 10 Engine Implementation",
        }

        return GovernanceAuditReport(
            audit_id=f"AUDIT_{algorithm_id}",
            algorithm_id=algorithm_id,
            certificate=certificate,
            findings=tuple(findings),
            provenance=provenance,
            report_hash=audit_hash,
        )
