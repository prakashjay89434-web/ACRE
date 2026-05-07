from pydantic import BaseModel
from typing import Optional, Any


class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None


class PlanResponse(BaseModel):
    plan_id: str
    steps: list[str]
    estimated_difficulty: float


class PipelineResponse(BaseModel):
    query: str
    plan_steps: list[str]
    code_output: str
    verification_score: int
    rag_score: float
    mcts_score: float


class StatusResponse(BaseModel):
    status: str
    message: str