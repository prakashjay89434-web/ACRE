from fastapi import WebSocket, WebSocketDisconnect
from graph import build_graph
import json

app_graph = build_graph()

async def websocket_pipeline(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            query = json.loads(data).get("query", "")

            await websocket.send_text(json.dumps({
                "type": "status",
                "message": f"Starting pipeline for: {query}"
            }))

            # Use the smart graph with classifier
            state = {
                "query": query,
                "plan": {},
                "current_step": 0,
                "code_result": {},
                "verification": {},
                "error": "",
                "query_type": ""
            }

            # Stream status updates
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": "🧠 Planner thinking..."
            }))

            result = app_graph.invoke(state)

            # Send plan if exists
            if result.get("plan", {}).get("steps"):
                await websocket.send_text(json.dumps({
                    "type": "plan",
                    "steps": result["plan"].get("steps", []),
                    "mcts_score": result["plan"].get("mcts_score", 0.0)
                }))

            # Send code/answer result
            code_result = result.get("code_result", {})
            await websocket.send_text(json.dumps({
                "type": "code",
                "code": code_result.get("code", ""),
                "output": code_result.get("stdout", ""),
                "error": code_result.get("error", False)
            }))

            # Send verification
            verification = result.get("verification", {})
            await websocket.send_text(json.dumps({
                "type": "result",
                "verification_score": verification.get("score", 0),
                "checks": verification.get("checks", {}),
                "message": "✅ Pipeline complete!"
            }))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))