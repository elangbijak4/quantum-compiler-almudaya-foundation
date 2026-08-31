"""
Module 6 Subpackage — Image Characterization & Signatures.
"""

from src.module6.image.signature import ImageSignature, compute_image_signature
from src.module6.image.collision import CollisionRecord, CollisionType, CollisionAnalyzer
from src.module6.image.characterization import EmpiricalImageSummary, EmpiricalImageCharacterizer

__all__ = [
    "ImageSignature",
    "compute_image_signature",
    "CollisionRecord",
    "CollisionType",
    "CollisionAnalyzer",
    "EmpiricalImageSummary",
    "EmpiricalImageCharacterizer",
]
