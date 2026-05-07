from fastapi import WebSocket, WebSocketDisconnect
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent
import json


async def websocket_pipeline(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive query from client
            data = await websocket.receive_text()
            query = json.loads(data).get("query", "")

            await websocket.send_text(json.dumps({
                "type": "status",
                "message": f"Starting pipeline for: {query}"
            }))

            # Step 1: Planner
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": "🧠 Planner thinking..."
            }))

            planner = PlannerAgent()
            state = {"query": query, "plan": {}, "current_step": 0,
                     "code_result": {}, "verification": {}, "error": ""}
            state = planner(state)

            await websocket.send_text(json.dumps({
                "type": "plan",
                "steps": state["plan"].get("steps", []),
                "mcts_score": state["plan"].get("mcts_score", 0)
            }))

            # Step 2: Coder
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": "💻 Coder generating and executing code..."
            }))

            coder = CoderAgent()
            state = coder(state)

            await websocket.send_text(json.dumps({
                "type": "code",
                "code": state["code_result"].get("code", ""),
                "output": state["code_result"].get("stdout", ""),
                "error": state["code_result"].get("error", False)
            }))

            # Step 3: Critic
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": "🔍 Critic verifying results..."
            }))

            critic = CriticAgent()
            state = critic(state)

            await websocket.send_text(json.dumps({
                "type": "result",
                "verification_score": state["verification"].get("score", 0),
                "checks": state["verification"].get("checks", {}),
                "message": "✅ Pipeline complete!"
            }))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))