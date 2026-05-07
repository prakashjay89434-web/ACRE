from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="ACRE - Agentic Code & Reasoning Engine",
    description="100% local multi-agent AI system",
    version="0.1.0"
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "ACRE",
        "version": "0.1.0",
        "status": "running",
        "endpoints": [
            "GET  /api/status",
            "POST /api/full_pipeline",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)