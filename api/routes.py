from fastapi import APIRouter, HTTPException
from api.schemas import QueryRequest, PipelineResponse, StatusResponse
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent
from graph import build_graph
import uuid

router = APIRouter()

# Initialize agents once
app_graph = build_graph()


@router.get("/status", response_model=StatusResponse)
def get_status():
    return StatusResponse(
        status="running",
        message="ACRE is up and running!"
    )


@router.post("/full_pipeline", response_model=PipelineResponse)
def full_pipeline(request: QueryRequest):
    try:
        result = app_graph.invoke({
            "query": request.query,
            "plan": {},
            "current_step": 0,
            "code_result": {},
            "verification": {},
            "error": ""
        })

        return PipelineResponse(
            query=result["query"],
            plan_steps=result["plan"].get("steps", []),
            code_output=result["code_result"].get("stdout", ""),
            verification_score=result["verification"].get("score", 0),
            rag_score=result["plan"].get("rag_score", 0.0),
            mcts_score=result["plan"].get("mcts_score", 0.0)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))