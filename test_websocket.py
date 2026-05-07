import asyncio
import websockets
import json


async def test_stream():
    uri = "ws://localhost:8000/stream"

    async with websockets.connect(uri, ping_timeout=300, close_timeout=300) as websocket:
        # Send query
        await websocket.send(json.dumps({
            "query": "Calculate the determinant of a 3x3 matrix"
        }))

        print("Query sent. Waiting for streaming response...\n")

        # Receive streaming messages
        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=120
                )
                data = json.loads(message)

                if data["type"] == "status":
                    print(f"⚡ {data['message']}")

                elif data["type"] == "plan":
                    print(f"\n📋 PLAN (MCTS score: {data['mcts_score']:.2f}):")
                    for step in data["steps"]:
                        print(f"   {step}")

                elif data["type"] == "code":
                    print(f"\n💻 CODE OUTPUT: {data['output'][:200]}")

                elif data["type"] == "result":
                    print(f"\n✅ VERIFICATION SCORE: {data['verification_score']}/100")
                    print(f"   Checks: {data['checks']}")
                    print("\nPipeline complete!")
                    break

                elif data["type"] == "error":
                    print(f"❌ Error: {data['message']}")
                    break

            except asyncio.TimeoutError:
                print("Timeout!")
                break


if __name__ == "__main__":
    asyncio.run(test_stream())