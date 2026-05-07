# ACRE — Agentic Code & Reasoning Engine

100% local multi-agent AI system. No external APIs. No cloud. Runs entirely on your machine.

## What it does
- Takes a math or code question
- Plans using Tree-of-Thoughts + MCTS
- Retrieves context using Self-Reflective RAG
- Generates and executes Python code in a sandbox
- Verifies results mathematically using sympy + numpy
- Returns verified answer via REST API

## Architecture
- **Planner Agent** — ToT + MCTS planning with RAG context
- **Coder Agent** — LLM code generation + sandbox execution
- **Critic Agent** — Math verification (NaN, Inf, stability checks)
- **RAG System** — Qdrant + BGE embeddings + self-reflection
- **MCTS** — UCB1 selection across 3 thought branches
- **FastAPI** — REST API with Swagger UI

## Stack
- LangGraph, Ollama, Qdrant, sentence-transformers
- sympy, numpy, scipy for math verification
- Unsloth LoRA fine-tuning (on Google Colab)
- Docker for containerization

## Quick Start
```bash
# Install Ollama and pull model
ollama pull qwen2.5-coder:1.5b

# Install dependencies
pip install -r requirements.txt

# Run the API
python main.py

# Open Swagger UI
http://localhost:8000/docs
```

## Test
```bash
python -m pytest tests/ -v
```

## Results
- 26/26 tests passing
- Verification score: 100/100
- Full pipeline: Plan → Code → Execute → Verify