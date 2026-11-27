"""Secure local registry for hosted and on-device chat models."""

import json
import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import keyring
from langchain_openai import ChatOpenAI


APP_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "don-os"
REGISTRY_PATH = APP_CONFIG_DIR / "models.json"
KEYRING_SERVICE = "don-os-models"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/v1"
MODEL_ID_PATTERN = re.compile(r"^[a-f0-9]{32}$")


class ModelRegistryError(ValueError):
    """Raised when model configuration or credentials cannot be safely used."""


def _ensure_config_dir() -> None:
    APP_CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(APP_CONFIG_DIR, 0o700)


def _read_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"active_model_id": "default", "models": []}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ModelRegistryError(f"Could not read the model registry: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("models", []), list):
        raise ModelRegistryError("The model registry has an invalid format.")
    data.setdefault("active_model_id", "default")
    data.setdefault("models", [])
    return data


def _write_registry(data: Dict[str, Any]) -> None:
    _ensure_config_dir()
    fd, temporary_path = tempfile.mkstemp(prefix=".models-", suffix=".json", dir=APP_CONFIG_DIR)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, REGISTRY_PATH)
        os.chmod(REGISTRY_PATH, 0o600)
    except OSError:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


def _validate_base_url(base_url: str, provider: str) -> str:
    value = base_url.strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ModelRegistryError("Endpoint URL must use http:// or https:// and include a hostname.")
    if parsed.username or parsed.password:
        raise ModelRegistryError("Do not put credentials in the endpoint URL; use the API key field.")
    if provider == "ollama" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ModelRegistryError("Ollama endpoints must use localhost or 127.0.0.1.")
    return value


def _public_model(model: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": model["id"],
        "name": model["name"],
        "provider": model["provider"],
        "model": model["model"],
        "base_url": model["base_url"],
        "has_api_key": bool(model.get("credential_id")),
    }


def list_models() -> Dict[str, Any]:
    registry = _read_registry()
    gemini_available = bool(os.getenv("GEMINI_API_KEY"))
    models = [
        {
            "id": "default",
            "name": "Gemini · automatic fallback",
            "provider": "gemini",
            "model": "automatic",
            "base_url": "",
            "has_api_key": gemini_available,
            "available": gemini_available,
        }
    ]
    models.extend(_public_model(item) for item in registry["models"])
    active_model_id = registry["active_model_id"]
    if active_model_id != "default" and not any(item["id"] == active_model_id for item in models):
        active_model_id = "default"
    return {"models": models, "active_model_id": active_model_id}


def add_model(
    name: str,
    provider: str,
    model_name: str,
    base_url: str,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    name = name.strip()
    model_name = model_name.strip()
    provider = provider.strip().lower()
    if not name or len(name) > 80:
        raise ModelRegistryError("Give this model a name between 1 and 80 characters.")
    if not model_name or len(model_name) > 160:
        raise ModelRegistryError("Enter a model identifier between 1 and 160 characters.")
    if provider not in {"openai-compatible", "ollama"}:
        raise ModelRegistryError("Choose a hosted API or Ollama local model.")
    if provider == "openai-compatible" and not (api_key or "").strip():
        raise ModelRegistryError("A hosted API model requires an API key.")
    base_url = _validate_base_url(base_url, provider)

    registry = _read_registry()
    if any(item["name"].casefold() == name.casefold() for item in registry["models"]):
        raise ModelRegistryError("A model with that name already exists.")

    model_id = uuid.uuid4().hex
    credential_id = model_id if provider == "openai-compatible" else None
    if credential_id:
        try:
            keyring.set_password(KEYRING_SERVICE, credential_id, api_key.strip())
        except Exception as error:
            raise ModelRegistryError(
                "The system credential store could not save this API key. Check that your desktop keyring is unlocked."
            ) from error

    item = {
        "id": model_id,
        "name": name,
        "provider": provider,
        "model": model_name,
        "base_url": base_url,
        "credential_id": credential_id,
    }
    try:
        registry["models"].append(item)
        _write_registry(registry)
    except Exception:
        if credential_id:
            try:
                keyring.delete_password(KEYRING_SERVICE, credential_id)
            except keyring.errors.PasswordDeleteError:
                pass
        raise
    return _public_model(item)


def remove_model(model_id: str) -> None:
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise ModelRegistryError("Invalid model identifier.")
    registry = _read_registry()
    remaining = [item for item in registry["models"] if item.get("id") != model_id]
    if len(remaining) == len(registry["models"]):
        raise ModelRegistryError("That model was not found.")
    removed = next(item for item in registry["models"] if item.get("id") == model_id)
    registry["models"] = remaining
    if registry["active_model_id"] == model_id:
        registry["active_model_id"] = "default"
    _write_registry(registry)
    credential_id = removed.get("credential_id")
    if credential_id:
        try:
            keyring.delete_password(KEYRING_SERVICE, credential_id)
        except keyring.errors.PasswordDeleteError:
            pass


def set_active_model(model_id: str) -> None:
    models = list_models()["models"]
    if not any(item["id"] == model_id for item in models):
        raise ModelRegistryError("Choose a configured model.")
    registry = _read_registry()
    registry["active_model_id"] = model_id
    _write_registry(registry)


def get_chat_model(model_id: str) -> ChatOpenAI:
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise ModelRegistryError("Choose a configured model.")
    registry = _read_registry()
    item = next((entry for entry in registry["models"] if entry.get("id") == model_id), None)
    if not item:
        raise ModelRegistryError("That model is no longer configured.")

    api_key = "ollama"
    if item["provider"] == "openai-compatible":
        try:
            api_key = keyring.get_password(KEYRING_SERVICE, item["credential_id"]) or ""
        except Exception as error:
            raise ModelRegistryError(
                "The system credential store could not read this API key. Check that your desktop keyring is unlocked."
            ) from error
        if not api_key:
            raise ModelRegistryError("The API key is missing. Remove and add this model again.")

    return ChatOpenAI(
        model=item["model"],
        api_key=api_key,
        base_url=item["base_url"],
        temperature=0.2,
        timeout=45,
        max_retries=0,
    )


def test_model(model_id: str) -> None:
    model = get_chat_model(model_id)
    model.invoke("Reply with exactly: OK")
