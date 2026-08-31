"""
Module 6 Stage 11 — Lineage Subpackage Exports.
"""

from src.module6.lineage.model import (
    HistoricalLineageRecord,
    LifecycleEvent,
    LineageTraceReport,
    RepositoryQueryResult,
    RepositoryIntegrityReport,
)
from src.module6.lineage.repository import HistoricalLineageRepository
from src.module6.lineage.evaluator import HistoricalLineageEvaluator
from src.module6.lineage.serialization import (
    serialize_historical_lineage_record,
    deserialize_historical_lineage_record,
    serialize_lifecycle_event,
    deserialize_lifecycle_event,
    serialize_lineage_trace_report,
    deserialize_lineage_trace_report,
    serialize_repository_query_result,
    deserialize_repository_query_result,
    serialize_repository_integrity_report,
    deserialize_repository_integrity_report,
)

__all__ = [
    "HistoricalLineageRecord",
    "LifecycleEvent",
    "LineageTraceReport",
    "RepositoryQueryResult",
    "RepositoryIntegrityReport",
    "HistoricalLineageRepository",
    "HistoricalLineageEvaluator",
    "serialize_historical_lineage_record",
    "deserialize_historical_lineage_record",
    "serialize_lifecycle_event",
    "deserialize_lifecycle_event",
    "serialize_lineage_trace_report",
    "deserialize_lineage_trace_report",
    "serialize_repository_query_result",
    "deserialize_repository_query_result",
    "serialize_repository_integrity_report",
    "deserialize_repository_integrity_report",
]
