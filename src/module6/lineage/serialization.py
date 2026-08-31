"""
Module 6 Stage 11 — Lineage Serialization.

Canonical JSON serialization and deserialization for HistoricalLineageRecord, LifecycleEvent,
LineageTraceReport, RepositoryQueryResult, and RepositoryIntegrityReport. Enforces deserialize(serialize(X)) == X.
"""

import json
from typing import Dict, Any
from src.module6.lineage.model import (
    HistoricalLineageRecord,
    LifecycleEvent,
    LineageTraceReport,
    RepositoryQueryResult,
    RepositoryIntegrityReport,
)


def serialize_historical_lineage_record(record: HistoricalLineageRecord) -> str:
    """Serializes HistoricalLineageRecord into canonical JSON string."""
    return json.dumps(record.to_dict(), indent=2, sort_keys=True)


def deserialize_historical_lineage_record(json_str: str) -> HistoricalLineageRecord:
    """Deserializes canonical JSON string into HistoricalLineageRecord."""
    data = json.loads(json_str)
    return HistoricalLineageRecord(
        record_id=data["record_id"],
        algorithm_id=data["algorithm_id"],
        audit_id=data["audit_id"],
        certificate_id=data["certificate_id"],
        circuit_id=data["circuit_id"],
        provenance_chain_hash=data["provenance_chain_hash"],
        lifecycle_event_id=data["lifecycle_event_id"],
        event_type=data["event_type"],
        event_sequence=data["event_sequence"],
        timestamp_identity=data["timestamp_identity"],
        source_program_hash=data.get("source_program_hash"),
        vocabulary_hash=data.get("vocabulary_hash"),
        baseline_hash=data.get("baseline_hash"),
        optimization_id=data.get("optimization_id"),
        quality_id=data.get("quality_id"),
        semantic_evidence_id=data.get("semantic_evidence_id"),
        governance_report_id=data.get("governance_report_id"),
        schema_version=data.get("schema_version", "1.1.0"),
        record_hash=data["record_hash"],
    )


def serialize_lifecycle_event(event: LifecycleEvent) -> str:
    """Serializes LifecycleEvent into canonical JSON string."""
    return json.dumps(event.to_dict(), indent=2, sort_keys=True)


def deserialize_lifecycle_event(json_str: str) -> LifecycleEvent:
    """Deserializes canonical JSON string into LifecycleEvent."""
    data = json.loads(json_str)
    return LifecycleEvent(
        event_id=data["event_id"],
        algorithm_id=data["algorithm_id"],
        event_type=data["event_type"],
        previous_state=data["previous_state"],
        new_state=data["new_state"],
        source_identity=data["source_identity"],
        evidence_identity=data["evidence_identity"],
        provenance=dict(data.get("provenance", {})),
        sequence=data.get("sequence", 0),
        schema_version=data.get("schema_version", "1.1.0"),
        deterministic_hash=data["deterministic_hash"],
    )


def serialize_lineage_trace_report(report: LineageTraceReport) -> str:
    """Serializes LineageTraceReport into canonical JSON string."""
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def deserialize_lineage_trace_report(json_str: str) -> LineageTraceReport:
    """Deserializes canonical JSON string into LineageTraceReport."""
    data = json.loads(json_str)
    records = [
        deserialize_historical_lineage_record(json.dumps(r_data)) for r_data in data["records"]
    ]
    events = [
        deserialize_lifecycle_event(json.dumps(e_data)) for e_data in data["events"]
    ]
    return LineageTraceReport(
        trace_id=data["trace_id"],
        algorithm_id=data["algorithm_id"],
        records=tuple(records),
        events=tuple(events),
        provenance=dict(data["provenance"]),
        report_hash=data["report_hash"],
        is_valid_chain=data.get("is_valid_chain", True),
    )


def serialize_repository_query_result(res: RepositoryQueryResult) -> str:
    """Serializes RepositoryQueryResult into canonical JSON string."""
    return json.dumps(res.to_dict(), indent=2, sort_keys=True)


def deserialize_repository_query_result(json_str: str) -> RepositoryQueryResult:
    """Deserializes canonical JSON string into RepositoryQueryResult."""
    data = json.loads(json_str)
    recs = [deserialize_historical_lineage_record(json.dumps(r)) for r in data["matching_records"]]
    evs = [deserialize_lifecycle_event(json.dumps(e)) for e in data["matching_events"]]
    return RepositoryQueryResult(
        query_id=data["query_id"],
        matching_records=tuple(recs),
        matching_events=tuple(evs),
        total_matches=data["total_matches"],
        query_hash=data["query_hash"],
    )


def serialize_repository_integrity_report(rep: RepositoryIntegrityReport) -> str:
    """Serializes RepositoryIntegrityReport into canonical JSON string."""
    return json.dumps(rep.to_dict(), indent=2, sort_keys=True)


def deserialize_repository_integrity_report(json_str: str) -> RepositoryIntegrityReport:
    """Deserializes canonical JSON string into RepositoryIntegrityReport."""
    data = json.loads(json_str)
    return RepositoryIntegrityReport(
        integrity_id=data["integrity_id"],
        is_integrity_valid=data["is_integrity_valid"],
        total_records=data["total_records"],
        total_events=data["total_events"],
        violations=tuple(data["violations"]),
        snapshot_hash=data["snapshot_hash"],
    )
