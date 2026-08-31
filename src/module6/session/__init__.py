"""
Module 6 Stage 6 — User Session Baseline & Lifecycle Subpackage.
"""

from src.module6.session.baseline import SessionBaseline, BaselineMode
from src.module6.session.resolver import EffectiveVocabularyResolver
from src.module6.session.lifecycle import SessionLifecycle
from src.module6.session.serialization import serialize_session_baseline, deserialize_session_baseline

__all__ = [
    "SessionBaseline",
    "BaselineMode",
    "EffectiveVocabularyResolver",
    "SessionLifecycle",
    "serialize_session_baseline",
    "deserialize_session_baseline",
]
