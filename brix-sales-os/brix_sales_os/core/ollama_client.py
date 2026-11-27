"""
brix_sales_os/core/ollama_client.py
==================================
Local AI inference client communicating with Ollama running on NVIDIA RTX 5060 GPU.
"""

import json
import httpx
from typing import Optional, Dict, Any
from brix_sales_os.config import settings
from brix_sales_os.core.security import sanitize_external_text

class OllamaClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.primary_model
        self.fallback_model = settings.fallback_model

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        timeout_seconds: int = 45
    ) -> str:
        """
        Executes a completion request against Ollama.
        """
        if settings.operating_mode == "SIMULATION":
            # Deterministic synthetic response in simulation mode
            if json_mode:
                return json.dumps({
                    "simulation": True,
                    "summary": "Simulated AI synthesis response for testing.",
                    "confidence": 0.95
                })
            return "Simulated AI response: All systems operating within normal parameters."

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_mode:
            payload["format"] = "json"

        endpoint = f"{self.base_url}/api/generate"
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(endpoint, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except Exception as e:
            # Fallback model attempt if primary model failed
            if self.fallback_model and self.fallback_model != self.model:
                try:
                    payload["model"] = self.fallback_model
                    with httpx.Client(timeout=timeout_seconds) as client:
                        resp = client.post(endpoint, json=payload)
                        resp.raise_for_status()
                        return resp.json().get("response", "").strip()
                except Exception:
                    pass
            raise RuntimeError(f"Ollama inference error on {self.base_url} with model {self.model}: {e}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout_seconds: int = 45
    ) -> Dict[str, Any]:
        """
        Generates structured JSON and safely parses it.
        """
        raw = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
            timeout_seconds=timeout_seconds
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Attempt to extract JSON substring if wrapped in markdown
            import re
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            return {"error": "Failed to parse structured JSON from LLM", "raw_output": raw}

ollama_client = OllamaClient()
