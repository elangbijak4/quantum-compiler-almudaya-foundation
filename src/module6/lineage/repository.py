"""
Module 6 Stage 11 — Persistent Append-Only Lineage Repository.

Provides HistoricalLineageRepository with local file persistence (save/load/reload),
atomic file writes, full 64-character SHA-256 integrity hashes, strict sequence verification,
cross-reference validation, and snapshot determinism.
"""

from typing import Dict, List, Tuple, Optional, Any
import hashlib
import json
import os
import tempfile
from src.module6.lineage.model import (
    HistoricalLineageRecord,
    LifecycleEvent,
    LineageTraceReport,
    RepositoryQueryResult,
    RepositoryIntegrityReport,
)
from src.module6.lineage.evaluator import HistoricalLineageEvaluator


class HistoricalLineageRepository:
    """
    Append-Only Deterministic Persistent Historical Lineage Repository.
    
    Enforces Invariants:
    1. Append-Only: Records and events can be created/appended, but NEVER modified or deleted.
    2. Local Persistence: Supports atomic save/load/reload to local JSON file storage.
    3. Full SHA-256 Integrity: Cryptographic verification across 64-character hex digests.
    4. Deterministic Snapshot: Produces process-restart identical snapshot identity hashes.
    5. Sequence Continuity & Origin: Strictly validates contiguous sequence progression starting at sequence 1.
    6. Cross-Reference Integrity: Validates record-to-event references and algorithm identity consistency.
    """

    SCHEMA_VERSION: str = "1.1.0"

    def __init__(self, storage_file_path: Optional[str] = None) -> None:
        self.storage_file_path: Optional[str] = storage_file_path
        self._records: Dict[str, HistoricalLineageRecord] = {}
        self._events: Dict[str, LifecycleEvent] = {}
        self._algorithm_records: Dict[str, List[str]] = {}
        self._algorithm_events: Dict[str, List[str]] = {}

    def append_record(self, record: HistoricalLineageRecord) -> HistoricalLineageRecord:
        """Appends a new historical lineage record. Raises ValueError if record_id already exists."""
        if record.record_id in self._records:
            raise ValueError(f"Append-Only Violation: Record {record.record_id} already exists in repository.")

        rec_hash = record.record_hash or record.compute_record_hash()
        final_record = HistoricalLineageRecord(
            record_id=record.record_id,
            algorithm_id=record.algorithm_id,
            audit_id=record.audit_id,
            certificate_id=record.certificate_id,
            circuit_id=record.circuit_id,
            provenance_chain_hash=record.provenance_chain_hash,
            lifecycle_event_id=record.lifecycle_event_id,
            event_type=record.event_type,
            event_sequence=record.event_sequence,
            timestamp_identity=record.timestamp_identity,
            source_program_hash=record.source_program_hash,
            vocabulary_hash=record.vocabulary_hash,
            baseline_hash=record.baseline_hash,
            optimization_id=record.optimization_id,
            quality_id=record.quality_id,
            semantic_evidence_id=record.semantic_evidence_id,
            governance_report_id=record.governance_report_id,
            schema_version=record.schema_version,
            record_hash=rec_hash,
        )

        self._records[final_record.record_id] = final_record
        if final_record.algorithm_id not in self._algorithm_records:
            self._algorithm_records[final_record.algorithm_id] = []
        self._algorithm_records[final_record.algorithm_id].append(final_record.record_id)
        return final_record

    def append_event(self, event: LifecycleEvent) -> LifecycleEvent:
        """Appends a new lifecycle event. Raises ValueError if event_id already exists."""
        if event.event_id in self._events:
            raise ValueError(f"Append-Only Violation: Event {event.event_id} already exists in repository.")

        ev_hash = event.deterministic_hash or event.compute_deterministic_hash()
        final_event = LifecycleEvent(
            event_id=event.event_id,
            algorithm_id=event.algorithm_id,
            event_type=event.event_type,
            previous_state=event.previous_state,
            new_state=event.new_state,
            source_identity=event.source_identity,
            evidence_identity=event.evidence_identity,
            provenance=dict(event.provenance),
            sequence=event.sequence,
            schema_version=event.schema_version,
            deterministic_hash=ev_hash,
        )

        self._events[final_event.event_id] = final_event
        if final_event.algorithm_id not in self._algorithm_events:
            self._algorithm_events[final_event.algorithm_id] = []
        self._algorithm_events[final_event.algorithm_id].append(final_event.event_id)
        return final_event

    def get_record(self, record_id: str) -> Optional[HistoricalLineageRecord]:
        """Retrieves a historical record by ID."""
        return self._records.get(record_id)

    def get_event(self, event_id: str) -> Optional[LifecycleEvent]:
        """Retrieves a lifecycle event by ID."""
        return self._events.get(event_id)

    def query(
        self,
        algorithm_id: Optional[str] = None,
        event_type: Optional[str] = None,
        certificate_id: Optional[str] = None,
    ) -> RepositoryQueryResult:
        """Executes read-only query over stored records and events."""
        matched_recs: List[HistoricalLineageRecord] = []
        matched_evs: List[LifecycleEvent] = []

        for r in self._records.values():
            if algorithm_id and r.algorithm_id != algorithm_id:
                continue
            if event_type and r.event_type != event_type:
                continue
            if certificate_id and r.certificate_id != certificate_id:
                continue
            matched_recs.append(r)

        for e in self._events.values():
            if algorithm_id and e.algorithm_id != algorithm_id:
                continue
            if event_type and e.event_type != event_type:
                continue
            matched_evs.append(e)

        matched_recs.sort(key=lambda x: (x.algorithm_id, x.event_sequence, x.record_id))
        matched_evs.sort(key=lambda x: (x.algorithm_id, x.sequence, x.event_id))

        q_raw = f"QUERY_{algorithm_id}_{event_type}_{certificate_id}_{len(matched_recs)}_{len(matched_evs)}"
        q_hash = hashlib.sha256(q_raw.encode("utf-8")).hexdigest()

        return RepositoryQueryResult(
            query_id=f"QRY_{q_hash[:16]}",
            matching_records=tuple(matched_recs),
            matching_events=tuple(matched_evs),
            total_matches=len(matched_recs) + len(matched_evs),
            query_hash=q_hash,
        )

    def trace_lineage(self, algorithm_id: str) -> LineageTraceReport:
        """Traces complete historical lineage for an algorithm with strict sequence verification."""
        rec_ids = self._algorithm_records.get(algorithm_id, [])
        ev_ids = self._algorithm_events.get(algorithm_id, [])

        recs = [self._records[rid] for rid in rec_ids if rid in self._records]
        evs = [self._events[eid] for eid in ev_ids if eid in self._events]

        is_valid = True
        if recs:
            if recs[0].event_sequence != 1:
                is_valid = False
            for i in range(len(recs) - 1):
                if recs[i+1].event_sequence != recs[i].event_sequence + 1:
                    is_valid = False
                    break

        if evs:
            if evs[0].sequence != 1:
                is_valid = False
            for i in range(len(evs) - 1):
                if evs[i+1].sequence != evs[i].sequence + 1:
                    is_valid = False
                    break

        recs_sorted = sorted(recs, key=lambda x: x.event_sequence)
        evs_sorted = sorted(evs, key=lambda x: x.sequence)

        t_raw = f"TRACE_{algorithm_id}_{len(recs)}_{len(evs)}_{is_valid}"
        t_hash = hashlib.sha256(t_raw.encode("utf-8")).hexdigest()

        return LineageTraceReport(
            trace_id=f"TRACE_{algorithm_id}",
            algorithm_id=algorithm_id,
            records=tuple(recs_sorted),
            events=tuple(evs_sorted),
            provenance={"algorithm_id": algorithm_id, "record_count": len(recs), "event_count": len(evs)},
            report_hash=t_hash,
            is_valid_chain=is_valid,
        )

    def verify_integrity(self) -> RepositoryIntegrityReport:
        """Verifies full SHA-256 hash integrity, sequence order, cross-references, and lifecycle transitions."""
        violations: List[str] = []

        # 1. Record hashes & Cross-references
        for r in self._records.values():
            expected = r.compute_record_hash()
            if r.record_hash != expected:
                violations.append(f"Record Hash Mismatch on {r.record_id}: got {r.record_hash}, expected {expected}")

            if r.lifecycle_event_id:
                linked_ev = self.get_event(r.lifecycle_event_id)
                if not linked_ev:
                    violations.append(f"BROKEN_REFERENCE: Record {r.record_id} references non-existent lifecycle event {r.lifecycle_event_id}")
                elif linked_ev.algorithm_id != r.algorithm_id:
                    violations.append(f"ALGORITHM_ID_MISMATCH: Record {r.record_id} algorithm_id ({r.algorithm_id}) mismatch with event {linked_ev.event_id} ({linked_ev.algorithm_id})")

        # 2. Event hashes & Transition validity
        for e in self._events.values():
            expected = e.compute_deterministic_hash()
            if e.deterministic_hash != expected:
                violations.append(f"Event Hash Mismatch on {e.event_id}: got {e.deterministic_hash}, expected {expected}")

            trans_res = HistoricalLineageEvaluator.validate_lifecycle_transition(e)
            if trans_res.classification == "INVALID":
                violations.append(f"INVALID_LIFECYCLE_TRANSITION: Event {e.event_id} has invalid transition from '{e.previous_state}' to '{e.new_state}'")

        # 3. Sequence continuity and origin check for records (in append insertion order)
        for alg_id, rec_ids in self._algorithm_records.items():
            recs = [self._records[rid] for rid in rec_ids if rid in self._records]
            if recs:
                if recs[0].event_sequence != 1:
                    violations.append(f"NON_ORIGIN_SEQUENCE: First record sequence for algorithm {alg_id} is {recs[0].event_sequence}, expected 1")
                for i in range(len(recs) - 1):
                    curr_seq = recs[i].event_sequence
                    next_seq = recs[i+1].event_sequence
                    if next_seq == curr_seq:
                        violations.append(f"DUPLICATE_SEQUENCE: Duplicate record sequence {next_seq} on algorithm {alg_id}")
                    elif next_seq < curr_seq:
                        violations.append(f"DECREASING_SEQUENCE: Decreasing record sequence {next_seq} after {curr_seq} on algorithm {alg_id}")
                    elif next_seq > curr_seq + 1:
                        violations.append(f"Sequence Continuity Gap on algorithm {alg_id}: record {recs[i+1].record_id} has sequence {next_seq}, expected {curr_seq + 1}")

        # 4. Sequence continuity and origin check for events (in append insertion order)
        for alg_id, ev_ids in self._algorithm_events.items():
            evs = [self._events[eid] for eid in ev_ids if eid in self._events]
            if evs:
                if evs[0].sequence != 1:
                    violations.append(f"NON_ORIGIN_SEQUENCE: First event sequence for algorithm {alg_id} is {evs[0].sequence}, expected 1")
                for i in range(len(evs) - 1):
                    curr_seq = evs[i].sequence
                    next_seq = evs[i+1].sequence
                    if next_seq == curr_seq:
                        violations.append(f"DUPLICATE_SEQUENCE: Duplicate event sequence {next_seq} on algorithm {alg_id}")
                    elif next_seq < curr_seq:
                        violations.append(f"DECREASING_SEQUENCE: Decreasing event sequence {next_seq} after {curr_seq} on algorithm {alg_id}")
                    elif next_seq > curr_seq + 1:
                        violations.append(f"SEQUENCE_GAP: Event sequence gap on algorithm {alg_id}: sequence {next_seq}, expected {curr_seq + 1}")

        snap_hash = self.get_snapshot_identity()
        integ_raw = f"INTEGRITY_{snap_hash}_{len(violations)}"
        integ_hash = hashlib.sha256(integ_raw.encode("utf-8")).hexdigest()

        return RepositoryIntegrityReport(
            integrity_id=f"INT_{integ_hash[:16]}",
            is_integrity_valid=len(violations) == 0,
            total_records=len(self._records),
            total_events=len(self._events),
            violations=tuple(violations),
            snapshot_hash=snap_hash,
        )

    def get_snapshot_identity(self) -> str:
        """Computes deterministic 64-character SHA-256 snapshot hash across all sorted record and event hashes."""
        sorted_recs = sorted(self._records.values(), key=lambda r: (r.algorithm_id, r.event_sequence, r.record_id))
        sorted_evs = sorted(self._events.values(), key=lambda e: (e.algorithm_id, e.sequence, e.event_id))

        sorted_rec_hashes = [r.record_hash for r in sorted_recs]
        sorted_ev_hashes = [e.deterministic_hash for e in sorted_evs]

        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "record_hashes": sorted_rec_hashes,
            "event_hashes": sorted_ev_hashes,
        }
        canonical_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def save(self, filepath: Optional[str] = None) -> str:
        """Saves repository contents to local file atomically."""
        target_path = filepath or self.storage_file_path
        if not target_path:
            raise ValueError("No storage file path specified for repository save.")

        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "snapshot_hash": self.get_snapshot_identity(),
            "records": [r.to_dict() for r in sorted(self._records.values(), key=lambda r: r.record_id)],
            "events": [e.to_dict() for e in sorted(self._events.values(), key=lambda e: e.event_id)],
        }
        content = json.dumps(payload, indent=2, sort_keys=True)

        dir_name = os.path.dirname(os.path.abspath(target_path))
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="repo_snap_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target_path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

        self.storage_file_path = target_path
        return target_path

    @classmethod
    def load(cls, filepath: str) -> "HistoricalLineageRepository":
        """Loads repository contents from local file and verifies integrity."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Repository file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            data = json.loads(content)
        except Exception as err:
            raise ValueError(f"REPOSITORY_INTEGRITY_FAILURE: Malformed JSON content in {filepath}: {err}")

        schema_ver = data.get("schema_version")
        if schema_ver != cls.SCHEMA_VERSION:
            raise ValueError(f"SCHEMA_INCOMPATIBILITY: Unsupported repository schema version {schema_ver}, expected {cls.SCHEMA_VERSION}")

        repo = cls(storage_file_path=filepath)

        for r_dict in data.get("records", []):
            rec = HistoricalLineageRecord(
                record_id=r_dict["record_id"],
                algorithm_id=r_dict["algorithm_id"],
                audit_id=r_dict["audit_id"],
                certificate_id=r_dict["certificate_id"],
                circuit_id=r_dict["circuit_id"],
                provenance_chain_hash=r_dict["provenance_chain_hash"],
                lifecycle_event_id=r_dict["lifecycle_event_id"],
                event_type=r_dict["event_type"],
                event_sequence=r_dict["event_sequence"],
                timestamp_identity=r_dict["timestamp_identity"],
                source_program_hash=r_dict.get("source_program_hash"),
                vocabulary_hash=r_dict.get("vocabulary_hash"),
                baseline_hash=r_dict.get("baseline_hash"),
                optimization_id=r_dict.get("optimization_id"),
                quality_id=r_dict.get("quality_id"),
                semantic_evidence_id=r_dict.get("semantic_evidence_id"),
                governance_report_id=r_dict.get("governance_report_id"),
                schema_version=r_dict.get("schema_version", cls.SCHEMA_VERSION),
                record_hash=r_dict.get("record_hash", ""),
            )
            if rec.record_hash != rec.compute_record_hash():
                raise ValueError(f"REPOSITORY_INTEGRITY_FAILURE: Corrupted record hash for {rec.record_id} in {filepath}")
            repo._records[rec.record_id] = rec
            if rec.algorithm_id not in repo._algorithm_records:
                repo._algorithm_records[rec.algorithm_id] = []
            repo._algorithm_records[rec.algorithm_id].append(rec.record_id)

        for e_dict in data.get("events", []):
            ev = LifecycleEvent(
                event_id=e_dict["event_id"],
                algorithm_id=e_dict["algorithm_id"],
                event_type=e_dict["event_type"],
                previous_state=e_dict["previous_state"],
                new_state=e_dict["new_state"],
                source_identity=e_dict["source_identity"],
                evidence_identity=e_dict["evidence_identity"],
                provenance=dict(e_dict.get("provenance", {})),
                sequence=e_dict.get("sequence", 0),
                schema_version=e_dict.get("schema_version", cls.SCHEMA_VERSION),
                deterministic_hash=e_dict.get("deterministic_hash", ""),
            )
            if ev.deterministic_hash != ev.compute_deterministic_hash():
                raise ValueError(f"REPOSITORY_INTEGRITY_FAILURE: Corrupted event hash for {ev.event_id} in {filepath}")
            repo._events[ev.event_id] = ev
            if ev.algorithm_id not in repo._algorithm_events:
                repo._algorithm_events[ev.algorithm_id] = []
            repo._algorithm_events[ev.algorithm_id].append(ev.event_id)

        recorded_snap = data.get("snapshot_hash")
        computed_snap = repo.get_snapshot_identity()
        if recorded_snap and recorded_snap != computed_snap:
            raise ValueError(f"REPOSITORY_INTEGRITY_FAILURE: Snapshot hash mismatch for {filepath}: recorded {recorded_snap}, computed {computed_snap}")

        return repo

    def reload(self) -> "HistoricalLineageRepository":
        """Reloads repository from disk to verify process restart equivalence."""
        if not self.storage_file_path:
            raise ValueError("Cannot reload repository without a storage file path.")
        return self.load(self.storage_file_path)
