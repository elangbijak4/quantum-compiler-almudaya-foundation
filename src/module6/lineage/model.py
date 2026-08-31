"""
Module 6 Stage 11 — Persistent Evolutionary Lifecycle Repository & Historical Audit Lineage Models.

Defines HistoricalLineageRecord, LifecycleEvent, LineageTraceReport,
RepositoryQueryResult, RepositoryIntegrityReport, and TransitionValidationResult.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import json
import hashlib


@dataclass(frozen=True)
class TransitionValidationResult:
    """
    Result model for lifecycle transition validation.
    """
    valid: bool
    classification: str  # "VALID", "INVALID", "INCONCLUSIVE"
    event_id: str
    previous_state: str
    new_state: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "classification": self.classification,
            "event_id": self.event_id,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class HistoricalLineageRecord:
    """
    Immutable historical lineage record representing a persisted compilation audit event.
    """
    record_id: str
    algorithm_id: str
    audit_id: str
    certificate_id: str
    circuit_id: str
    provenance_chain_hash: str
    lifecycle_event_id: str
    event_type: str
    event_sequence: int
    timestamp_identity: str
    source_program_hash: Optional[str] = None
    vocabulary_hash: Optional[str] = None
    baseline_hash: Optional[str] = None
    optimization_id: Optional[str] = None
    quality_id: Optional[str] = None
    semantic_evidence_id: Optional[str] = None
    governance_report_id: Optional[str] = None
    schema_version: str = "1.1.0"
    record_hash: str = ""

    def __post_init__(self) -> None:
        if not self.record_hash:
            object.__setattr__(self, "record_hash", self.compute_record_hash())

    def compute_record_hash(self) -> str:
        raw_dict = {
            "record_id": self.record_id,
            "algorithm_id": self.algorithm_id,
            "audit_id": self.audit_id,
            "certificate_id": self.certificate_id,
            "circuit_id": self.circuit_id,
            "provenance_chain_hash": self.provenance_chain_hash,
            "lifecycle_event_id": self.lifecycle_event_id,
            "event_type": self.event_type,
            "event_sequence": self.event_sequence,
            "timestamp_identity": self.timestamp_identity,
            "source_program_hash": self.source_program_hash,
            "vocabulary_hash": self.vocabulary_hash,
            "baseline_hash": self.baseline_hash,
            "optimization_id": self.optimization_id,
            "quality_id": self.quality_id,
            "semantic_evidence_id": self.semantic_evidence_id,
            "governance_report_id": self.governance_report_id,
            "schema_version": self.schema_version,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "algorithm_id": self.algorithm_id,
            "audit_id": self.audit_id,
            "certificate_id": self.certificate_id,
            "circuit_id": self.circuit_id,
            "provenance_chain_hash": self.provenance_chain_hash,
            "lifecycle_event_id": self.lifecycle_event_id,
            "event_type": self.event_type,
            "event_sequence": self.event_sequence,
            "timestamp_identity": self.timestamp_identity,
            "source_program_hash": self.source_program_hash,
            "vocabulary_hash": self.vocabulary_hash,
            "baseline_hash": self.baseline_hash,
            "optimization_id": self.optimization_id,
            "quality_id": self.quality_id,
            "semantic_evidence_id": self.semantic_evidence_id,
            "governance_report_id": self.governance_report_id,
            "schema_version": self.schema_version,
            "record_hash": self.record_hash,
        }


@dataclass(frozen=True)
class LifecycleEvent:
    """
    Immutable lifecycle transition event record.
    """
    event_id: str
    algorithm_id: str
    event_type: str
    previous_state: str
    new_state: str
    source_identity: str
    evidence_identity: str
    provenance: Dict[str, Any] = field(default_factory=dict)
    sequence: int = 0
    schema_version: str = "1.1.0"
    deterministic_hash: str = ""

    def __post_init__(self) -> None:
        if not self.deterministic_hash:
            object.__setattr__(self, "deterministic_hash", self.compute_deterministic_hash())

    def compute_deterministic_hash(self) -> str:
        raw_dict = {
            "event_id": self.event_id,
            "algorithm_id": self.algorithm_id,
            "event_type": self.event_type,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "source_identity": self.source_identity,
            "evidence_identity": self.evidence_identity,
            "provenance": self.provenance,
            "sequence": self.sequence,
            "schema_version": self.schema_version,
        }
        canonical_str = json.dumps(raw_dict, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "algorithm_id": self.algorithm_id,
            "event_type": self.event_type,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "source_identity": self.source_identity,
            "evidence_identity": self.evidence_identity,
            "provenance": dict(self.provenance),
            "sequence": self.sequence,
            "schema_version": self.schema_version,
            "deterministic_hash": self.deterministic_hash,
        }


@dataclass(frozen=True)
class LineageTraceReport:
    """
    Master Stage 11 Lineage Trace Report representing end-to-end historical provenance.
    """
    trace_id: str
    algorithm_id: str
    records: Tuple[HistoricalLineageRecord, ...]
    events: Tuple[LifecycleEvent, ...]
    provenance: Dict[str, Any] = field(default_factory=dict)
    report_hash: str = ""
    is_valid_chain: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "algorithm_id": self.algorithm_id,
            "records": [r.to_dict() for r in self.records],
            "events": [e.to_dict() for e in self.events],
            "provenance": dict(self.provenance),
            "report_hash": self.report_hash,
            "is_valid_chain": self.is_valid_chain,
        }


@dataclass(frozen=True)
class RepositoryQueryResult:
    """
    Result model for repository queries.
    """
    query_id: str
    matching_records: Tuple[HistoricalLineageRecord, ...]
    matching_events: Tuple[LifecycleEvent, ...]
    total_matches: int
    query_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "matching_records": [r.to_dict() for r in self.matching_records],
            "matching_events": [e.to_dict() for e in self.matching_events],
            "total_matches": self.total_matches,
            "query_hash": self.query_hash,
        }


@dataclass(frozen=True)
class RepositoryIntegrityReport:
    """
    Report model for repository integrity audits.
    """
    integrity_id: str
    is_integrity_valid: bool
    total_records: int
    total_events: int
    violations: Tuple[str, ...]
    snapshot_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "integrity_id": self.integrity_id,
            "is_integrity_valid": self.is_integrity_valid,
            "total_records": self.total_records,
            "total_events": self.total_events,
            "violations": list(self.violations),
            "snapshot_hash": self.snapshot_hash,
        }
