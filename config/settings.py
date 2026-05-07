from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="ACRE")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)

    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen2.5-coder:1.5b")

    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection: str = Field(default="acre_knowledge")

    sandbox_timeout: int = Field(default=30)
    sandbox_memory_mb: int = Field(default=512)

    log_level: str = Field(default="DEBUG")
    log_file: str = Field(default="logs/acre.log")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()