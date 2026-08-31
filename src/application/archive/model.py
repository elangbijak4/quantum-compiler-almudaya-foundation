"""
Application / Product Layer — Research Run / Output Archive Abstractions.

Provides ResearchRunStatus, ArchivedArtifact, ResearchRun, and OutputArchiveManager establishing
the persistent, researcher-facing Output Archive without mutating Core authority or state.
"""

from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import os
from typing import Dict, List, Tuple, Optional, Any


class ResearchRunStatus(str, Enum):
    """Research Run Status Classification."""

    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ArchivedArtifact:
    """Archived Computational Artifact Representation."""

    artifact_id: str
    artifact_type: str
    hash: str
    stage: str
    status: str
    parent_artifact_id: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Returns non-sensitive dictionary representation."""
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "parent_artifact_id": self.parent_artifact_id,
            "hash": self.hash,
            "stage": self.stage,
            "status": self.status,
            "provenance": self.provenance,
        }


@dataclass
class ResearchRun:
    """Research Run Persistent Record."""

    run_id: str
    created_at: str
    status: ResearchRunStatus
    backend_id: str = "LOCAL_REFERENCE"
    shots: int = 1000
    verification_policy_id: str = "POLICY_DEFAULT"
    source_code: Optional[str] = None
    artifacts: List[ArchivedArtifact] = field(default_factory=list)
    lineage_reference: Optional[str] = None

    def to_manifest_dict(self) -> Dict[str, Any]:
        """Returns canonical manifest dictionary for manifest.json."""
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "status": self.status.value,
            "backend_id": self.backend_id,
            "shots": self.shots,
            "verification_policy_id": self.verification_policy_id,
            "source_code": self.source_code,
            "artifacts_count": len(self.artifacts),
            "artifacts": [a.to_dict() for a in self.artifacts],
            "lineage_reference": self.lineage_reference,
            "manifest_hash": "",
        }


class OutputArchiveManager:
    """
    Application-level manager for persistent Output/ Research Run Archives.
    
    Invariants:
    1. Research-Facing Materialization: Output archive is NOT a computational authority.
    2. Immutability: Finalized ResearchRun records are strictly read-only.
    3. Security: Zero raw credential leakage in manifests or archived payloads.
    4. Core Boundary: Zero Core mutation; operates strictly above Application Contract.
    """

    def __init__(self, base_dir: str = "Output") -> None:
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        self._active_runs: Dict[str, ResearchRun] = {}

    def start_research_run(
        self,
        run_id: str,
        backend_id: str = "LOCAL_REFERENCE",
        shots: int = 1000,
        verification_policy_id: str = "POLICY_DEFAULT",
        source_code: Optional[str] = None,
    ) -> ResearchRun:
        """Initializes a new active ResearchRun."""
        created_at = datetime.now(timezone.utc).isoformat()
        run = ResearchRun(
            run_id=run_id,
            created_at=created_at,
            status=ResearchRunStatus.PARTIAL,
            backend_id=backend_id,
            shots=shots,
            verification_policy_id=verification_policy_id,
            source_code=source_code,
        )
        self._active_runs[run_id] = run
        return run

    def record_artifact(self, run_id: str, artifact: ArchivedArtifact) -> None:
        """Appends an authoritative artifact to an active ResearchRun."""
        run = self._active_runs.get(run_id)
        if not run:
            raise KeyError(f"No active ResearchRun found with run_id '{run_id}'.")
        run.artifacts.append(artifact)

    def finalize_research_run(
        self,
        run_id: str,
        final_status: ResearchRunStatus = ResearchRunStatus.COMPLETED,
        lineage_reference: Optional[str] = None,
    ) -> str:
        """
        Finalizes an active ResearchRun, writing manifest.json and stage artifacts to disk.
        Returns the absolute directory path of the archived ResearchRun.
        """
        run = self._active_runs.get(run_id)
        if not run:
            raise KeyError(f"No active ResearchRun found with run_id '{run_id}'.")

        run.status = final_status
        if lineage_reference:
            run.lineage_reference = lineage_reference

        # Format folder name: Run_<timestamp>_<run_id>
        ts_str = datetime.fromisoformat(run.created_at).strftime("%Y%m%d_%H%M%S")
        folder_name = f"Run_{ts_str}_{run.run_id}"
        run_dir = os.path.join(self.base_dir, folder_name)
        os.makedirs(run_dir, exist_ok=True)

        manifest_data = run.to_manifest_dict()
        manifest_json_str = json.dumps(manifest_data, indent=2, sort_keys=True)
        manifest_hash = hashlib.sha256(manifest_json_str.encode("utf-8")).hexdigest()
        manifest_data["manifest_hash"] = manifest_hash

        # Write manifest.json
        manifest_path = os.path.join(run_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        # Write human-readable README.md report
        readme_path = os.path.join(run_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(self._generate_readme(run, manifest_hash))

        # Remove from active memory tracking once written
        del self._active_runs[run_id]
        return run_dir

    def load_research_run(self, run_dir: str) -> Dict[str, Any]:
        """
        Read-only deserialization of an archived ResearchRun.
        Triggers ZERO compilation, simulation, or execution side-effects.
        """
        manifest_path = os.path.join(run_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"No manifest.json found in research run directory '{run_dir}'.")

        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _generate_readme(self, run: ResearchRun, manifest_hash: str) -> str:
        """Generates human-readable README.md summary for ResearchRun folder."""
        lines = [
            f"# Quantum Compiler Research Run Report — `{run.run_id}`",
            "",
            f"- **Created At**: `{run.created_at}`",
            f"- **Status**: `{run.status.value}`",
            f"- **Backend Target**: `{run.backend_id}`",
            f"- **Shots**: `{run.shots}`",
            f"- **Verification Policy**: `{run.verification_policy_id}`",
            f"- **Manifest Hash**: `{manifest_hash}`",
            "",
            "## Archived Stage Artifacts",
            "",
            "| Stage | Artifact ID | Type | Parent ID | Hash | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for a in run.artifacts:
            parent = a.parent_artifact_id or "-"
            lines.append(f"| `{a.stage}` | `{a.artifact_id}` | `{a.artifact_type}` | `{parent}` | `{a.hash[:16]}...` | `{a.status}` |")

        lines.extend([
            "",
            "---",
            "*This report is a read-only researcher-facing materialization of an authoritative computational process.*",
        ])
        return "\n".join(lines)
