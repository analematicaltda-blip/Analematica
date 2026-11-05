from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
from datetime import datetime, timezone

class OptimizationDomain(str, Enum):
    TOOL_CALLING_ACCURACY = "TOOL_CALLING_ACCURACY"
    LATENCY_REDUCTION = "LATENCY_REDUCTION"
    HALLUCINATION_ELIMINATION = "HALLUCINATION_ELIMINATION"
    SCHEMA_COMPLIANCE = "SCHEMA_COMPLIANCE"

class PromotionReadinessLevel(str, Enum):
    CANDIDATE_TRAINED = "CANDIDATE_TRAINED"
    BENCHMARK_PASSED = "BENCHMARK_PASSED"
    REGRESSION_TEST_CLEARED = "REGRESSION_TEST_CLEARED"
    REQUIRES_ARCHITECT_APPROVAL = "REQUIRES_ARCHITECT_APPROVAL"

class ModelCandidatePromotionContract(BaseModel):
    """CONTRATO DE ENTREGA DE SOUP HACIA JARVI Y EL ROUTER"""
    model_config = ConfigDict(frozen=True)

    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    target_military_rank: str = Field(...)
    base_model_id: str = Field(...)
    adapter_artifact_uri: str = Field(...)
    optimization_domain: OptimizationDomain = Field(...)
    dataset_training_samples: int = Field(...)
    prior_accuracy_percentage: float = Field(...)
    candidate_accuracy_percentage: float = Field(...)
    backend_72_tests_passed: bool = Field(default=True)
    readiness_level: PromotionReadinessLevel = Field(default=PromotionReadinessLevel.REQUIRES_ARCHITECT_APPROVAL)
    activation_command: str = Field(...)