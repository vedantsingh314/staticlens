from pydantic import BaseModel
from typing import List, Optional, Any


class CyclomaticComplexity(BaseModel):
    max: int
    average: float


class HalsteadMetrics(BaseModel):
    n1_distinct_operators: int
    n2_distinct_operands: int
    N1_total_operators: int
    N2_total_operands: int
    vocabulary: int
    program_length: int
    volume: float
    difficulty: float
    effort: float
    estimated_bugs: float


class OOPMetrics(BaseModel):
    number_of_classes: int
    number_of_methods: int
    number_of_attributes: int
    inheritance_relationships: int
    avg_methods_per_class: float
    avg_attributes_per_class: float
    method_to_attribute_ratio: float


class FileMetrics(BaseModel):
    cyclomatic_complexity: CyclomaticComplexity
    halstead: HalsteadMetrics
    oop_metrics: OOPMetrics


class FileAnalysisResult(BaseModel):
    file: str
    language: str
    metrics: FileMetrics

class AnalysisSummary(BaseModel):
    total_files_scanned: int
    total_files_analyzed: int
    average_complexity: float

class RepositoryAnalysisResponse(BaseModel):
    repo_url: str
    summary: AnalysisSummary
    files: List[FileAnalysisResult]