"""
Module 7 Stage 1 — Historical Backend Registry Engine.

Provides HistoricalBackendRegistry implementing BackendRegistryProtocol.
Enforces immutable capability snapshots, multi-version capability preservation,
retirement (no physical deletion), thread-safety, and canonical SHA-256 integrity verification.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import hashlib
import json
import threading
from src.module7.model import (
    BackendCapabilityModel,
    ExecutionFailureCategory,
)
from src.module7.interfaces import BackendRegistryProtocol


class HistoricalBackendRegistry(BackendRegistryProtocol):
    """
    Append-Only Deterministic Historical Backend Registry.
    
    Enforces Invariants:
    1. Provider Neutrality: Core registry logic operates without third-party SDK dependencies.
    2. Immutability: Stored capability snapshots CANNOT be modified. Updates produce new versions.
    3. No Physical Deletion: Backends are retired/deactivated, NEVER physically erased.
    4. Deterministic Identity: Unique capability snapshots identified by 64-char SHA-256 digests.
    5. Zero Module 6 Mutation: Operating registry DOES NOT alter Module 6 evolutionary state.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._capabilities_by_key: Dict[Tuple[str, str], BackendCapabilityModel] = {}
        self._capabilities_by_hash: Dict[str, BackendCapabilityModel] = {}
        self._active_version: Dict[str, str] = {}  # backend_id -> latest active capability_version
        self._retired_backends: Set[str] = set()  # retired backend_ids

    def register_backend(self, capability: BackendCapabilityModel) -> BackendCapabilityModel:
        """
        Registers a new backend capability model.
        Raises ValueError if version conflict or malformed capability.
        """
        capability.validate()

        with self._lock:
            key = (capability.backend_id, capability.capability_version)
            cap_hash = capability.capability_hash or capability.compute_capability_hash()

            # Check if identical hash already registered (idempotent)
            if key in self._capabilities_by_key:
                existing = self._capabilities_by_key[key]
                if existing.capability_hash != cap_hash:
                    raise ValueError(
                        f"CAPABILITY_VERSION_CONFLICT: Backend '{capability.backend_id}' version '{capability.capability_version}' "
                        f"already registered with different capability hash {existing.capability_hash} (got {cap_hash})."
                    )
                return existing

            # Store immutable capability snapshot
            self._capabilities_by_key[key] = capability
            self._capabilities_by_hash[cap_hash] = capability
            self._active_version[capability.backend_id] = capability.capability_version

            # If registered backend was previously retired, reactivate latest version
            if capability.backend_id in self._retired_backends:
                self._retired_backends.remove(capability.backend_id)

            return capability

    def get_backend(self, backend_id: str, capability_version: Optional[str] = None) -> Optional[BackendCapabilityModel]:
        """
        Retrieves a backend capability snapshot by backend_id and optional capability_version.
        If capability_version is omitted, returns the latest active version.
        """
        with self._lock:
            if capability_version is not None:
                return self._capabilities_by_key.get((backend_id, capability_version))

            latest_version = self._active_version.get(backend_id)
            if not latest_version:
                return None
            return self._capabilities_by_key.get((backend_id, latest_version))

    def get_by_hash(self, capability_hash: str) -> Optional[BackendCapabilityModel]:
        """Retrieves a backend capability model directly by its 64-character SHA-256 hash."""
        with self._lock:
            return self._capabilities_by_hash.get(capability_hash)

    def contains_backend(self, backend_id: str, capability_version: Optional[str] = None) -> bool:
        """Checks if backend_id (and optional version) is registered."""
        return self.get_backend(backend_id, capability_version) is not None

    def is_retired(self, backend_id: str) -> bool:
        """Checks if a backend has been retired."""
        with self._lock:
            return backend_id in self._retired_backends

    def retire_backend(self, backend_id: str) -> bool:
        """
        Retires/deactivates a backend without physically deleting historical capability snapshots.
        Returns True if backend was active and is now retired, False if not found.
        """
        with self._lock:
            if backend_id not in self._active_version:
                return False
            self._retired_backends.add(backend_id)
            return True

    def list_backends(self, include_retired: bool = False) -> Tuple[BackendCapabilityModel, ...]:
        """
        Lists registered backend capability models.
        By default, returns active backends. If include_retired is True, returns all historical snapshots.
        """
        with self._lock:
            res: List[BackendCapabilityModel] = []
            for (b_id, ver), cap in sorted(self._capabilities_by_key.items()):
                if not include_retired and b_id in self._retired_backends:
                    continue
                # If only active listed, only include latest active version for each active backend
                if not include_retired and self._active_version.get(b_id) != ver:
                    continue
                res.append(cap)
            return tuple(res)
