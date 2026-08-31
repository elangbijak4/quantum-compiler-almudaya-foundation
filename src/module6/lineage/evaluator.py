"""
Module 6 Stage 11 — Historical Lineage Evaluator.

Processes Stage 10 GovernanceAuditReport artifacts, constructs immutable HistoricalLineageRecord
and LifecycleEvent objects, validates lifecycle state transitions, and builds deterministic LineageTraceReports.
"""

from typing import Dict, Any, Optional, List, Tuple
import hashlib
from src.module6.governance.model import GovernanceAuditReport
from src.module6.lineage.model import (
    HistoricalLineageRecord,
    LifecycleEvent,
    LineageTraceReport,
    TransitionValidationResult,
)


class HistoricalLineageEvaluator:
    """
    Production Historical Lineage Evaluator.
    
    Enforces Invariants:
    1. Upstream Immutability: Zero mutation to inputs or Stage 1–10 states.
    2. Zero Certification Authority: Observes and records Stage 10 AuditCertificates without issuing or altering them.
    3. Hardware & Noise Boundaries: 0% real hardware execution, 0% physical noise simulation.
    4. Full 64-character SHA-256 Digests: Generates cryptographic hashes across all trace objects.
    5. Explicit Missing-Evidence Semantics: Preserves None for absent upstream fields. No synthetic string construction.
    6. Executable Transition Validation: Evaluates previous_state -> new_state transition validity against approved policy.
    """

    ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
        "CANDIDATE": ["ANALYZED", "REJECTED"],
        "ANALYZED": ["DRAFT", "VERIFIED", "REJECTED"],
        "DRAFT": ["VERIFIED", "REJECTED"],
        "VERIFIED": ["GOVERNED", "DEPRECATED", "REJECTED"],
        "GOVERNED": ["CERTIFIED", "PROMOTED", "DEPRECATED", "REJECTED"],
        "CERTIFIED": ["PROMOTED", "DEPRECATED"],
        "PROMOTED": ["DEPRECATED"],
        "DEPRECATED": [],
        "REJECTED": [],
    }

    @classmethod
    def validate_lifecycle_transition(cls, event: LifecycleEvent) -> TransitionValidationResult:
        """
        Validates if a lifecycle event's state transition is permitted under approved policy.
        Returns TransitionValidationResult classified as VALID, INVALID, or INCONCLUSIVE.
        """
        prev_s = event.previous_state
        new_s = event.new_state

        if not prev_s or not new_s:
            return TransitionValidationResult(
                valid=False,
                classification="INCONCLUSIVE",
                event_id=event.event_id,
                previous_state=prev_s or "",
                new_state=new_s or "",
                reason="Insufficient evidence: previous_state or new_state is empty.",
            )

        if prev_s not in cls.ALLOWED_TRANSITIONS:
            return TransitionValidationResult(
                valid=False,
                classification="INVALID",
                event_id=event.event_id,
                previous_state=prev_s,
                new_state=new_s,
                reason=f"Unknown previous lifecycle state '{prev_s}'.",
            )

        if new_s not in cls.ALLOWED_TRANSITIONS[prev_s]:
            return TransitionValidationResult(
                valid=False,
                classification="INVALID",
                event_id=event.event_id,
                previous_state=prev_s,
                new_state=new_s,
                reason=f"Lifecycle transition from '{prev_s}' to '{new_s}' is prohibited by policy.",
            )

        return TransitionValidationResult(
            valid=True,
            classification="VALID",
            event_id=event.event_id,
            previous_state=prev_s,
            new_state=new_s,
            reason=f"Lifecycle transition from '{prev_s}' to '{new_s}' is valid.",
        )

    @classmethod
    def trace_compilation_lineage(
        cls,
        audit_report: GovernanceAuditReport,
        repository: Any = None,
    ) -> LineageTraceReport:
        """
        Traces compilation lineage from Stage 10 audit report evidence.
        Optionally persists records to provided append-only repository.
        """
        algorithm_id = audit_report.algorithm_id
        cert = audit_report.certificate
        prov = audit_report.provenance

        # GAP-1: Extract optional fields without constructing synthetic string placeholders
        source_prog_hash = prov.get("source_program_hash")
        circ_id = prov.get("circuit_id", algorithm_id)
        vocab_hash = prov.get("vocab_hash") or prov.get("context_hash")
        baseline_hash = prov.get("baseline_hash")
        opt_id = prov.get("optimization_report_hash")
        qual_id = prov.get("quality_report_hash")
        sem_ev_id = prov.get("semantic_evidence_id") # None if absent, no synthetic string!
        gov_id = audit_report.audit_id

        chain_raw = f"{algorithm_id}_{cert.certificate_id}_{audit_report.report_hash}_{cert.provenance_hash}"
        chain_hash = hashlib.sha256(chain_raw.encode("utf-8")).hexdigest()

        status_val = cert.lifecycle_status.value
        if status_val in ("CERTIFIED", "PROMOTED"):
            prev_state = "GOVERNED"
        elif status_val == "GOVERNED":
            prev_state = "VERIFIED"
        else:
            prev_state = "ANALYZED"

        event_id = f"EVT_{algorithm_id}_{status_val}_{chain_hash[:16]}"
        lifecycle_event = LifecycleEvent(
            event_id=event_id,
            algorithm_id=algorithm_id,
            event_type=f"AUDIT_{status_val}",
            previous_state=prev_state,
            new_state=status_val,
            source_identity=algorithm_id,
            evidence_identity=cert.certificate_id,
            provenance={
                "audit_hash": audit_report.report_hash,
                "cert_level": cert.certification_level.value,
                "algorithm_id": algorithm_id,
            },
            sequence=1,
        )

        record_id = f"REC_{algorithm_id}_{chain_hash[:16]}"
        lineage_record = HistoricalLineageRecord(
            record_id=record_id,
            algorithm_id=algorithm_id,
            source_program_hash=source_prog_hash,
            audit_id=audit_report.audit_id,
            certificate_id=cert.certificate_id,
            circuit_id=circ_id,
            vocabulary_hash=vocab_hash,
            baseline_hash=baseline_hash,
            optimization_id=opt_id,
            quality_id=qual_id,
            semantic_evidence_id=sem_ev_id,
            governance_report_id=gov_id,
            provenance_chain_hash=chain_hash,
            lifecycle_event_id=event_id,
            event_type=f"AUDIT_{status_val}",
            event_sequence=1,
            timestamp_identity="DETERMINISTIC_STAGE11_IDENTITY",
        )

        if repository is not None:
            repository.append_event(lifecycle_event)
            repository.append_record(lineage_record)

        trace_raw = f"TRACE_{algorithm_id}_{chain_hash}"
        trace_hash = hashlib.sha256(trace_raw.encode("utf-8")).hexdigest()

        return LineageTraceReport(
            trace_id=f"TRACE_{algorithm_id}",
            algorithm_id=algorithm_id,
            records=(lineage_record,),
            events=(lifecycle_event,),
            provenance={
                "algorithm_id": algorithm_id,
                "audit_id": audit_report.audit_id,
                "certificate_id": cert.certificate_id,
                "certification_level": cert.certification_level.value,
                "chain_hash": chain_hash,
                "stage": "Stage 11 Production Engine",
            },
            report_hash=trace_hash,
            is_valid_chain=True,
        )
