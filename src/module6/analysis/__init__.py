"""
Module 6 Analysis Subpackage.

Provides Stage 1, Stage 2, Stage 3, Stage 4, Stage 5, Stage 6, and Stage 7 analysis entrypoints and reports.
"""

from src.module6.analysis.stage1 import analyze_classical_algorithm_stage1
from src.module6.analysis.stage2 import analyze_compiler_image_stage2
from src.module6.analysis.stage3 import analyze_compiler_mapping_stage3
from src.module6.analysis.stage4 import analyze_compiler_mapping_stage4
from src.module6.analysis.stage5 import analyze_evolving_compiler_stage5, Stage5AnalysisReport
from src.module6.analysis.stage6 import analyze_stage6_evolution_and_feasibility, Stage6AnalysisReport
from src.module6.analysis.stage7 import analyze_stage7_resolution_and_control, Stage7AnalysisReport

__all__ = [
    "analyze_classical_algorithm_stage1",
    "analyze_compiler_image_stage2",
    "analyze_compiler_mapping_stage3",
    "analyze_compiler_mapping_stage4",
    "analyze_evolving_compiler_stage5",
    "Stage5AnalysisReport",
    "analyze_stage6_evolution_and_feasibility",
    "Stage6AnalysisReport",
    "analyze_stage7_resolution_and_control",
    "Stage7AnalysisReport",
]
