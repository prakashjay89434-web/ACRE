from abc import ABC, abstractmethod
from typing import Any
import logging
import time

logger = logging.getLogger(__name__)


class BaseAgent(ABC):

    def __init__(self, name: str):
        self.name = name
        self._call_count = 0
        self._total_latency = 0.0
        logger.debug(f"Agent initialized: {self.name}")

    @abstractmethod
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        self._call_count += 1
        logger.info(f"[{self.name}] Starting. Call #{self._call_count}")

        try:
            result = self.run(state)
        except Exception as e:
            logger.error(f"[{self.name}] Error: {e}")
            result = {**state, "error": str(e), "failed_agent": self.name}

        elapsed = time.perf_counter() - start
        self._total_latency += elapsed
        logger.info(f"[{self.name}] Done in {elapsed:.3f}s")
        return result

    def get_stats(self) -> dict:
        return {
            "agent": self.name,
            "call_count": self._call_count,
            "avg_latency_s": round(
                self._total_latency / self._call_count if self._call_count else 0, 4
            ),
        }