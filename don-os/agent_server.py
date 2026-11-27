"""
agent_server.py

FastAPI backend server exposing the Central Agent Brain to the Electron desktop interface.
Runs on http://127.0.0.1:8765
"""

import os
import asyncio
import re
import sqlite3
import subprocess
import threading
import tempfile
from queue import Empty, Queue
import json
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic import SecretStr
from typing import Optional, Dict, Any, List

from agent import CentralAgentBrain
from tools.hardware_controller import (
    get_battery_status,
    get_screen_brightness,
    get_cpu_info,
    set_screen_brightness,
    lock_desktop_screen,
)
import tools.memory_tool as memory_tool
import tools.time_tool as time_tool
import tools.tts_speaker as tts_speaker
from tools.memory_tool import list_all_memories, search_notes, get_recent_chat_history, remember, forget, save_note, record_chat_turn
from tools.time_tool import list_reminders, add_reminder, cancel_reminder
from tools.desktop_workflow_tool import get_clipboard_text
from tools.tts_speaker import speak_text_sync, stop_current_speech
from tools.mcp_controller import (
    fetch_server_tools_async,
    load_mcp_config,
    load_mcp_config_strict,
    save_mcp_config,
)
from tools.acp_controller import load_acp_config, list_acp_servers
from tools.model_registry import (
    ModelRegistryError,
    add_model,
    list_models,
    remove_model,
    set_active_model,
    test_model,
)
from tools.local_model_manager import (
    cancel_local_model_download,
    connect_existing_local_model,
    connect_installed_local_model,
    get_local_model_catalog,
    get_local_model_download,
    scan_local_model_hardware,
    start_local_model_download,
)



app = FastAPI(title="PA Assistant Brain API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LocalModelRequest(BaseModel):
    catalog_id: str = Field(min_length=1, max_length=80)


class ExistingLocalModelRequest(BaseModel):
    model_name: str = Field(min_length=1, max_length=160)


class ModelRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    provider: str
    model: str = Field(min_length=1, max_length=160)
    base_url: str = Field(min_length=1, max_length=500)
    api_key: Optional[SecretStr] = None


class ActiveModelRequest(BaseModel):
    model_id: str


# Global Brain Instance
brain = CentralAgentBrain(session_id="electron_ui")


@app.get("/api/models")
def get_models_endpoint():
    try:
        return list_models()
    except ModelRegistryError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/api/models")
def add_model_endpoint(req: ModelRequest):
    try:
        model = add_model(
            req.name,
            req.provider,
            req.model,
            req.base_url,
            req.api_key.get_secret_value() if req.api_key else None,
        )
    except ModelRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except OSError as error:
        raise HTTPException(status_code=500, detail="Could not save the model configuration.") from error
    return {"model": model}


@app.delete("/api/models/{model_id}")
def delete_model_endpoint(model_id: str):
    try:
        remove_model(model_id)
    except ModelRegistryError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except OSError as error:
        raise HTTPException(status_code=500, detail="Could not remove the model configuration.") from error
    return {"status": "removed"}


@app.put("/api/models/active")
def set_active_model_endpoint(req: ActiveModelRequest):
    try:
        set_active_model(req.model_id)
    except ModelRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except OSError as error:
        raise HTTPException(status_code=500, detail="Could not save the selected model.") from error
    return {"active_model_id": req.model_id}


@app.post("/api/models/{model_id}/test")
def test_model_endpoint(model_id: str):
    try:
        test_model(model_id)
    except ModelRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Connection failed. Verify the model name, API key, endpoint, and that Ollama is running if this is a local model.",
        ) from error
    return {"status": "connected"}


@app.get("/api/models/local/hardware")
def scan_local_model_hardware_endpoint():
    return scan_local_model_hardware()


@app.get("/api/models/local/catalog")
def get_local_model_catalog_endpoint():
    return get_local_model_catalog()


@app.post("/api/models/local/download")
def download_local_model_endpoint(req: LocalModelRequest):
    try:
        return start_local_model_download(req.catalog_id)
    except ModelRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/models/local/download/{job_id}")
def get_local_model_download_endpoint(job_id: str):
    try:
        return get_local_model_download(job_id)
    except ModelRegistryError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.delete("/api/models/local/download/{job_id}")
def cancel_local_model_download_endpoint(job_id: str):
    try:
        return cancel_local_model_download(job_id)
    except ModelRegistryError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/models/local/connect")
def connect_installed_local_model_endpoint(req: LocalModelRequest):
    try:
        return {"model": connect_installed_local_model(req.catalog_id)}
    except ModelRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/models/local/connect-existing")
def connect_existing_local_model_endpoint(req: ExistingLocalModelRequest):
    try:
        return {"model": connect_existing_local_model(req.model_name)}
    except ModelRegistryError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _init_server_tables():
    """Ensure chat_sessions table exists in memory database."""
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error creating chat_sessions table: {e}")

_init_server_tables()


# ==========================================================================
# Request Models
# ==========================================================================
class ChatRequest(BaseModel):
    prompt: str
    speak: Optional[bool] = False
    session_id: Optional[str] = "default"
    voice_mode: Optional[bool] = False
    mcp_servers: Optional[List[str]] = None
    model_id: Optional[str] = "default"


class MCPServerRequest(BaseModel):
    name: str
    command: str = ""
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    transport: str = "stdio"
    url: str = ""
    headers: Dict[str, str] = Field(default_factory=dict)


class SpeakRequest(BaseModel):
    text: str


class SaveMemoryRequest(BaseModel):
    key: str
    information: str
    category: Optional[str] = "general"


class DeleteMemoryRequest(BaseModel):
    key: str


class SaveNoteRequest(BaseModel):
    title: str
    content: str
    tags: Optional[str] = ""


class DeleteNoteRequest(BaseModel):
    title: str


class AddReminderRequest(BaseModel):
    time_spec: str
    message: str


class DeleteReminderRequest(BaseModel):
    id: int


class SetBrightnessRequest(BaseModel):
    percentage: int


class SetVolumeRequest(BaseModel):
    percentage: int


class SessionCreateRequest(BaseModel):
    id: str
    title: str


class SessionRenameRequest(BaseModel):
    id: str
    title: str


class VoiceConfigRequest(BaseModel):
    voice: str
    rate: Optional[str] = "+0%"


@app.get("/api/health")
def health_check():
    return {"status": "online", "model": "gemini-3.8-flash"}


@app.get("/api/mcp/servers")
def get_mcp_servers():
    try:
        servers = load_mcp_config_strict().get("mcpServers", {})
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Could not read MCP configuration: {error}") from error

    return {
        "servers": [
            {
                "name": name,
                "command": (
                    os.path.basename(str(config.get("command", "")))
                    if config.get("command")
                    else str(config.get("url", "MCP server")).split("/")[2]
                    if "://" in str(config.get("url", ""))
                    else "MCP server"
                ),
                "transport": "http" if config.get("transport") == "http" or config.get("type") == "http" else "stdio",
                "auth_configured": any(
                    key.lower() in {"authorization", "x-api-key", "api-key"}
                    for key in config.get("headers", {})
                ) if isinstance(config.get("headers", {}), dict) else False,
                "env_keys": sorted(config.get("env", {}).keys())
                if isinstance(config.get("env", {}), dict) else [],
            }
            for name, config in servers.items()
            if isinstance(config, dict)
        ]
    }


@app.post("/api/mcp/servers")
def add_mcp_server(req: MCPServerRequest):
    name = req.name.strip()
    command = req.command.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", name):
        raise HTTPException(
            status_code=400,
            detail="Connector name must be 1–64 letters, numbers, dots, underscores, or hyphens.",
        )
    if req.transport not in {"stdio", "http"}:
        raise HTTPException(status_code=400, detail="Connector transport must be stdio or http.")
    if req.transport == "stdio" and (not command or len(command) > 1024 or "\x00" in command):
        raise HTTPException(status_code=400, detail="A valid command path or executable is required.")
    if req.transport == "http":
        from urllib.parse import urlsplit
        endpoint = urlsplit(req.url.strip())
        if endpoint.scheme not in {"http", "https"} or not endpoint.hostname or endpoint.username:
            raise HTTPException(status_code=400, detail="HTTP connectors require a valid http:// or https:// endpoint.")
        if len(req.url) > 2048 or "\x00" in req.url:
            raise HTTPException(status_code=400, detail="Connector endpoint exceeds the supported size.")
    if any(not isinstance(arg, str) or "\x00" in arg for arg in req.args):
        raise HTTPException(status_code=400, detail="Connector arguments must be valid text values.")
    if len(req.args) > 128 or any(len(arg) > 4096 for arg in req.args):
        raise HTTPException(status_code=400, detail="Connector arguments exceed the supported size.")
    if any(
        not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
        or not isinstance(value, str)
        or "\x00" in value
        for key, value in req.env.items()
    ):
        raise HTTPException(status_code=400, detail="Environment variables must use valid names and text values.")
    if any(
        not re.fullmatch(r"[A-Za-z0-9-]+", key)
        or not isinstance(value, str)
        or len(value) > 8192
        or "\x00" in value
        for key, value in req.headers.items()
    ):
        raise HTTPException(status_code=400, detail="HTTP headers must use valid names and text values.")

    try:
        config = load_mcp_config_strict()
        servers = config.setdefault("mcpServers", {})
        if name in servers:
            raise HTTPException(status_code=409, detail=f"Connector '{name}' already exists.")
        if req.transport == "http":
            servers[name] = {
                "type": "http",
                "transport": "http",
                "url": req.url.strip(),
                "headers": req.headers,
            }
        else:
            servers[name] = {"command": command, "args": req.args, "env": req.env}
        save_mcp_config(config)
    except HTTPException:
        raise
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Could not save MCP connector: {error}") from error
    return {"name": name, "status": "configured"}


@app.delete("/api/mcp/servers/{server_name}")
def delete_mcp_server(server_name: str):
    try:
        config = load_mcp_config_strict()
        servers = config.get("mcpServers", {})
        if server_name not in servers:
            raise HTTPException(status_code=404, detail=f"Connector '{server_name}' was not found.")
        del servers[server_name]
        save_mcp_config(config)
    except HTTPException:
        raise
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Could not remove MCP connector: {error}") from error
    return {"name": server_name, "status": "removed"}


@app.post("/api/mcp/servers/{server_name}/test")
def test_mcp_server(server_name: str):
    try:
        config = load_mcp_config_strict().get("mcpServers", {})
        server_config = config.get(server_name)
        if not isinstance(server_config, dict):
            raise HTTPException(status_code=404, detail=f"Connector '{server_name}' was not found.")
        tools = asyncio.run(
            fetch_server_tools_async(server_name, server_config, raise_on_error=True)
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return {
        "name": server_name,
        "status": "connected",
        "tools": [
            {"name": item["raw_name"], "description": item.get("description", "")}
            for item in tools
        ],
    }


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    selected_servers = req.mcp_servers or []
    if len(selected_servers) > 5:
        raise HTTPException(status_code=400, detail="Attach no more than five MCP connectors per message.")
    try:
        configured_servers = load_mcp_config_strict().get("mcpServers", {})
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Could not read MCP configuration: {error}") from error
    unknown_servers = sorted(set(selected_servers) - set(configured_servers))
    if unknown_servers:
        raise HTTPException(status_code=400, detail=f"Unknown MCP connector(s): {', '.join(unknown_servers)}")

    session_id = req.session_id or "default"
    result = brain.execute_prompt(
        req.prompt,
        voice_mode=req.voice_mode,
        mcp_servers=selected_servers,
        model_id=req.model_id or "default",
    )

    # Record turn into SQLite chat history
    try:
        record_chat_turn(session_id, "user", req.prompt)
        if result.get("response"):
            record_chat_turn(session_id, "assistant", result["response"])
        
        # Ensure session exists in chat_sessions table with a friendly title
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM chat_sessions WHERE id = ?", (session_id,))
            existing = cursor.fetchone()
            if not existing:
                title = req.prompt.strip()[:35] + ("..." if len(req.prompt.strip()) > 35 else "")
                cursor.execute(
                    "INSERT INTO chat_sessions (id, title, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (session_id, title)
                )
            else:
                cursor.execute(
                    "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (session_id,)
                )
            conn.commit()
    except Exception as e:
        print(f"Error persisting session chat turn: {e}")

    # Optional speech readback in non-blocking thread
    if req.speak and result.get("status") == "success":
        threading.Thread(target=speak_text_sync, args=(result["response"],), daemon=True).start()

    return result


@app.post("/api/chat/stream")
def stream_chat_endpoint(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    selected_servers = req.mcp_servers or []
    if len(selected_servers) > 5:
        raise HTTPException(status_code=400, detail="Attach no more than five MCP connectors per message.")
    try:
        configured_servers = load_mcp_config_strict().get("mcpServers", {})
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Could not read MCP configuration: {error}") from error
    unknown_servers = sorted(set(selected_servers) - set(configured_servers))
    if unknown_servers:
        raise HTTPException(status_code=400, detail=f"Unknown MCP connector(s): {', '.join(unknown_servers)}")

    events: Queue[Dict[str, Any]] = Queue()
    session_id = req.session_id or "default"

    def report_progress(message: str) -> None:
        events.put({"type": "status", "message": message})

    def run_agent() -> None:
        try:
            result = brain.execute_prompt(
                req.prompt,
                progress_callback=report_progress,
                voice_mode=req.voice_mode,
                mcp_servers=selected_servers,
                model_id=req.model_id or "default",
            )
            try:
                record_chat_turn(session_id, "user", req.prompt)
                if result.get("response"):
                    record_chat_turn(session_id, "assistant", result["response"])

                with sqlite3.connect(memory_tool.DB_PATH) as conn:
                    title = req.prompt.strip()[:35] + ("..." if len(req.prompt.strip()) > 35 else "")
                    conn.execute(
                        "INSERT INTO chat_sessions (id, title, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
                        "ON CONFLICT(id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP",
                        (session_id, title),
                    )
                    conn.commit()
            except (sqlite3.Error, OSError) as error:
                print(f"Error updating streamed chat session: {error}")

            if req.speak and result.get("status") == "success":
                threading.Thread(target=speak_text_sync, args=(result["response"],), daemon=True).start()
        except Exception as error:
            print(f"Error processing streamed chat request: {error}")
            result = {
                "response": f"AI Engine error: {error}",
                "tool_calls_executed": [],
                "status": "error",
            }

        events.put({"type": "result", "data": result})

    threading.Thread(target=run_agent, daemon=True).start()

    def stream_events():
        while True:
            try:
                event = events.get(timeout=15)
            except Empty:
                yield json.dumps({"type": "keepalive"}) + "\n"
                continue

            yield json.dumps(event) + "\n"
            if event["type"] == "result":
                break

    return StreamingResponse(
        stream_events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ==========================================================================
# Multi-Agent Fleet Orchestrator Endpoints (Autonomous Swarm Execution)
# ==========================================================================

from multi_agent_core.orchestrator import FleetOrchestrator
from agent import CORE_TOOLS, _get_llm

@app.post("/api/fleet/stream")
def stream_fleet_endpoint(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    events: Queue[Dict[str, Any]] = Queue()
    session_id = req.session_id or "default"

    def on_fleet_event(event: Dict[str, Any]):
        etype = event.get("type")
        msg = ""
        if etype == "plan_created":
            msg = f"Fleet Plan Generated: {event['total_agents']} specialized agents assigned."
        elif etype == "agent_spawned":
            msg = f"Deployed {event['role']}: {event['directive'][:50]}..."
        elif etype == "agent_tool_call":
            msg = f"{event['role']} calling tool '{event['tool']}'..."
        elif etype == "agent_completed":
            msg = f"Completed {event['role']} subtask."
        elif etype == "synthesis_started":
            msg = "Synthesizing fleet deliverables into final executive brief..."
        else:
            msg = event.get("message", f"Fleet execution: {etype}")

        events.put({"type": "status", "message": msg, "fleet_event": event})

    def run_fleet():
        try:
            llm = _get_llm("gemini-3.1-flash-lite")
            orchestrator = FleetOrchestrator(model_instance=llm, all_tools=CORE_TOOLS)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                orchestrator.execute_mission(req.prompt, event_callback=on_fleet_event)
            )
            loop.close()

            try:
                record_chat_turn(session_id, "user", f"[Fleet Mission] {req.prompt}")
                if result.get("response"):
                    record_chat_turn(session_id, "assistant", result["response"])
            except Exception as e:
                print(f"Error persisting session chat turn: {e}")

            data = {
                "response": result.get("response", ""),
                "status": "success",
                "tool_calls_executed": [f"{a['role']}: {a['directive'][:40]}" for a in result.get("agent_details", [])],
                "fleet_summary": {
                    "agents_deployed": result.get("agents_deployed", 0),
                    "pages_created": len(result.get("blackboard_pages", [])),
                    "elapsed_seconds": result.get("elapsed_seconds", 0),
                    "agent_details": result.get("agent_details", [])
                }
            }
        except Exception as error:
            print(f"Error in multi-agent fleet execution: {error}")
            data = {
                "response": f"Multi-Agent Fleet execution error: {error}",
                "status": "error",
                "tool_calls_executed": []
            }
        events.put({"type": "result", "data": data})

    threading.Thread(target=run_fleet, daemon=True).start()

    def stream_events():
        while True:
            try:
                event = events.get(timeout=25)
            except Empty:
                yield json.dumps({"type": "keepalive"}) + "\n"
                continue

            yield json.dumps(event) + "\n"
            if event["type"] == "result":
                break

    return StreamingResponse(
        stream_events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ==========================================================================
# Chat Sessions & Conversation History Endpoints (ChatGPT & Claude Style)
# ==========================================================================
@app.get("/api/sessions")
def get_sessions():
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, updated_at FROM chat_sessions ORDER BY updated_at DESC LIMIT 50")
            rows = cursor.fetchall()
            return {"sessions": [{"id": r[0], "title": r[1], "updated_at": r[2]} for r in rows]}
    except Exception as e:
        return {"sessions": [], "error": str(e)}


@app.post("/api/sessions/create")
def create_session(req: SessionCreateRequest):
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            conn.execute(
                "INSERT INTO chat_sessions (id, title, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(id) DO UPDATE SET title = excluded.title, updated_at = CURRENT_TIMESTAMP",
                (req.id, req.title)
            )
            conn.commit()
        return {"status": "success", "id": req.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/rename")
def rename_session(req: SessionRenameRequest):
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            conn.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (req.title, req.id)
            )
            conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()
        return {"status": "deleted", "id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/messages")
def get_session_messages(session_id: str):
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, timestamp FROM chat_history WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            return {"messages": [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in rows]}
    except Exception as e:
        return {"messages": [], "error": str(e)}


# ==========================================================================
# Editable Memories Endpoints
# ==========================================================================
@app.get("/api/memories/raw")
def get_raw_memories():
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, key, information, category, updated_at FROM memories ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return {"memories": [{"id": r[0], "key": r[1], "information": r[2], "category": r[3], "updated_at": r[4]} for r in rows]}
    except Exception as e:
        return {"memories": [], "error": str(e)}


@app.post("/api/memories/save")
def save_memory_endpoint(req: SaveMemoryRequest):
    try:
        res = remember.invoke({"key": req.key, "information": req.information, "category": req.category or "general"})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memories/delete")
def delete_memory_endpoint(req: DeleteMemoryRequest):
    try:
        res = forget.invoke({"key": req.key})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================================
# Editable Notes Endpoints
# ==========================================================================
@app.get("/api/notes/raw")
def get_raw_notes():
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content, tags, updated_at FROM notes ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return {"notes": [{"id": r[0], "title": r[1], "content": r[2], "tags": r[3], "updated_at": r[4]} for r in rows]}
    except Exception as e:
        return {"notes": [], "error": str(e)}


@app.post("/api/notes/save")
def save_note_endpoint(req: SaveNoteRequest):
    try:
        res = save_note.invoke({"title": req.title, "content": req.content, "tags": req.tags or ""})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notes/delete")
def delete_note_endpoint(req: DeleteNoteRequest):
    try:
        with sqlite3.connect(memory_tool.DB_PATH) as conn:
            conn.execute("DELETE FROM notes WHERE title = ?", (req.title,))
            conn.commit()
        return {"status": "success", "deleted": req.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================================
# Editable Reminders Endpoints
# ==========================================================================
@app.get("/api/reminders/raw")
def get_raw_reminders():
    try:
        with sqlite3.connect(time_tool.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, message, due_time, status, created_at FROM reminders ORDER BY id DESC")
            rows = cursor.fetchall()
            return {"reminders": [{"id": r[0], "message": r[1], "due_time": r[2], "status": r[3], "created_at": r[4]} for r in rows]}
    except Exception as e:
        return {"reminders": [], "error": str(e)}


@app.post("/api/reminders/add")
def add_reminder_endpoint(req: AddReminderRequest):
    try:
        res = add_reminder.invoke({"time_spec": req.time_spec, "message": req.message})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reminders/delete")
def delete_reminder_endpoint(req: DeleteReminderRequest):
    try:
        res = cancel_reminder.invoke({"reminder_id": req.id})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================================
# Hardware & Audio Controls
# ==========================================================================
def _get_audio_volume() -> int:
    try:
        res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True)
        if res.returncode == 0 and "Volume:" in res.stdout:
            parts = res.stdout.strip().split()
            vol = float(parts[1])
            return min(100, int(round(vol * 100)))
    except Exception:
        pass
    return 75


def _set_audio_volume(percentage: int) -> bool:
    try:
        val = max(0, min(100, percentage))
        res = subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{val/100:.2f}"], capture_output=True)
        if res.returncode == 0:
            return True
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{val}%"], capture_output=True)
        return True
    except Exception:
        return False


@app.get("/api/hardware/status")
def hardware_status():
    brightness_str = get_screen_brightness.invoke({})
    brightness_num = 100
    try:
        import re
        match = re.search(r'(\d+)%', brightness_str)
        if match:
            brightness_num = int(match.group(1))
        else:
            digits = "".join(filter(str.isdigit, brightness_str))
            if digits:
                brightness_num = min(100, int(digits))
    except Exception:
        brightness_num = 100

    return {
        "battery": get_battery_status.invoke({}),
        "brightness": brightness_num,
        "volume": _get_audio_volume(),
        "cpu": get_cpu_info.invoke({}),
    }


@app.post("/api/hardware/brightness")
def set_brightness_endpoint(req: SetBrightnessRequest):
    try:
        res = set_screen_brightness.invoke({"percentage": req.percentage})
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/hardware/volume")
def set_volume_endpoint(req: SetVolumeRequest):
    ok = _set_audio_volume(req.percentage)
    return {"status": "success" if ok else "error", "volume": req.percentage}


# ==========================================================================
# Voice Profile Configuration
# ==========================================================================
@app.get("/api/voice/config")
def get_voice_config():
    return {
        "voice": getattr(tts_speaker, "DEFAULT_VOICE", "en-US-AvaNeural"),
        "rate": getattr(tts_speaker, "DEFAULT_RATE", "+5%"),
        "available_voices": [
            {"id": "en-US-AvaNeural", "name": "Ava (Mature Girl ~25y, Soft & Expressive)"},
            {"id": "en-US-JennyNeural", "name": "Jenny (Conversational & Natural)"},
            {"id": "en-US-EmmaNeural", "name": "Emma (Warm & Articulate)"},
            {"id": "en-GB-SoniaNeural", "name": "Sonia (British Sophisticated)"},
            {"id": "en-US-AnaNeural", "name": "Ana (Gentle & Calm)"}
        ]
    }


@app.post("/api/voice/config")
def set_voice_config(req: VoiceConfigRequest):
    tts_speaker.DEFAULT_VOICE = req.voice
    if req.rate:
        tts_speaker.DEFAULT_RATE = req.rate
    return {"status": "success", "voice": tts_speaker.DEFAULT_VOICE, "rate": tts_speaker.DEFAULT_RATE}


@app.get("/api/status")
def status_endpoint():
    try:
        cfg = load_mcp_config()
        mcp_count = len(cfg.get("mcpServers", {}))
    except Exception:
        mcp_count = 0

    try:
        acp_cfg = load_acp_config()
        acp_count = len(acp_cfg.get("acpServers", {}))
    except Exception:
        acp_count = 0

    return {
        "status": "online",
        "mcp_servers": mcp_count,
        "acp_servers": acp_count,
        "battery": get_battery_status.invoke({}),
        "brightness": get_screen_brightness.invoke({}),
        "cpu": get_cpu_info.invoke({})
    }


@app.get("/api/acp/servers")
def acp_servers_endpoint():
    return {"servers": load_acp_config().get("acpServers", {})}



@app.get("/api/memories")
def memories_endpoint():
    return {"memories": list_all_memories.invoke({})}


@app.get("/api/history")
def history_endpoint():
    return {"history": get_recent_chat_history("electron_ui", limit=20)}


@app.post("/api/speak")
def speak_endpoint(req: SpeakRequest):
    if req.text.strip():
        threading.Thread(target=speak_text_sync, args=(req.text.strip(),), daemon=True).start()
        return {"status": "speaking"}
    return {"status": "empty"}


@app.get("/api/speech/status")
def speech_status_endpoint():
    return tts_speaker.get_speech_status()


@app.get("/api/reminders")
def reminders_endpoint():
    try:
        return {"reminders": list_reminders.invoke({})}
    except Exception as e:
        return {"reminders": f"Error loading reminders: {e}"}


@app.get("/api/notes")
def notes_endpoint(q: str = ""):
    try:
        return {"notes": search_notes.invoke({"query": q})}
    except Exception as e:
        return {"notes": f"Error loading notes: {e}"}


@app.get("/api/clipboard")
def clipboard_endpoint():
    try:
        return {"clipboard": get_clipboard_text.invoke({})}
    except Exception as e:
        return {"clipboard": f"Error: {e}"}


@app.post("/api/lock")
def lock_endpoint():
    try:
        res = lock_desktop_screen.invoke({})
        return {"status": "success", "result": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/clear")
def clear_endpoint():
    brain.history.clear()
    return {"status": "cleared"}


# ==========================================================================
# Google Assistant / Alexa Style High-Speed Voice & Transcription Services
# ==========================================================================
_whisper_model = None
_whisper_lock = threading.Lock()


def get_whisper_model():
    """Lazy-loads and caches local Faster-Whisper base.en model for sub-second offline ASR."""
    global _whisper_model
    with _whisper_lock:
        if _whisper_model is None:
            from faster_whisper import WhisperModel
            _whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
        return _whisper_model


@app.post("/api/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Transcribes recorded audio from the desktop interface with high accuracy and low latency.
    Includes acoustic echo suppression to prevent Whisper from hearing and processing assistant TTS speech.
    """
    try:
        # 1. Hardware acoustic echo prevention check
        speech_status = tts_speaker.get_speech_status()
        if speech_status.get("active_or_cooldown"):
            print("[ASR] Audio chunk dropped: TTS speech active or reverberation cooldown active.")
            return {"text": "", "status": "echo_ignored"}

        content = await file.read()
        if not content:
            return {"text": "", "status": "empty"}

        suffix = ".webm" if "webm" in (file.content_type or "") else ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(content)
            tmp.flush()

            model = get_whisper_model()
            segments, info = model.transcribe(tmp.name, beam_size=1)
            text = " ".join([s.text for s in segments]).strip()

            # 2. Textual echo filter: discard if text matches recent assistant speech
            if text:
                lower_text = re.sub(r'[^a-z0-9 ]', '', text.lower()).strip()
                for spoken in speech_status.get("recent_texts", []):
                    clean_spoken = re.sub(r'[^a-z0-9 ]', '', spoken.lower()).strip()
                    if len(lower_text) >= 8 and (lower_text in clean_spoken or clean_spoken in lower_text):
                        print(f"[ASR] Dropped self-hearing echo match: '{text}' matches assistant speech.")
                        return {"text": "", "status": "echo_dropped"}

            return {
                "text": text,
                "language": info.language if info else "en",
                "status": "success"
            }
    except Exception as e:
        print(f"[ASR Error]: {e}")
        return {"text": "", "error": str(e), "status": "error"}


@app.post("/api/stop_speech")
def stop_speech_endpoint():
    """Interrupts active speech for immediate Google/Alexa barge-in functionality."""
    stop_current_speech()
    return {"status": "stopped"}


# ==============================================================================
# Professional Code Review & Git Diff Studio Endpoints
# ==============================================================================

class CodeReviewDiffRequest(BaseModel):
    filepath: Optional[str] = None

class CodeReviewAuditRequest(BaseModel):
    filepath: Optional[str] = None
    diff_context: Optional[str] = None

@app.get("/api/review/status")
def review_status_endpoint():
    """Returns list of modified and untracked files with change statistics from git."""
    try:
        # Get status with short format
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=os.path.abspath("."),
            capture_output=True,
            text=True
        )
        lines = status_proc.stdout.strip().split("\n") if status_proc.stdout.strip() else []
        files = []
        for line in lines:
            if not line:
                continue
            status_code = line[:2].strip()
            filepath = line[3:].strip()
            # If renamed, take the target
            if " -> " in filepath:
                filepath = filepath.split(" -> ")[1].strip()
            files.append({
                "path": filepath,
                "status": status_code,
                "display_status": "Modified" if "M" in status_code else ("Untracked" if "?" in status_code else "Changed")
            })

        # Summary diffstat
        diff_stat_proc = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=os.path.abspath("."),
            capture_output=True,
            text=True
        )
        return {
            "files": files,
            "count": len(files),
            "summary_stat": diff_stat_proc.stdout.strip()
        }
    except Exception as e:
        return {"error": str(e), "files": [], "count": 0}


@app.post("/api/review/diff")
def review_diff_endpoint(req: CodeReviewDiffRequest):
    """Retrieves full git diff for a specific file or whole working tree."""
    try:
        cmd = ["git", "diff"]
        if req.filepath:
            cmd.extend(["--", req.filepath])
        
        proc = subprocess.run(
            cmd,
            cwd=os.path.abspath("."),
            capture_output=True,
            text=True
        )
        diff_text = proc.stdout

        # If file is untracked and has no diff, read the file content as added lines
        if not diff_text and req.filepath and os.path.exists(req.filepath):
            with open(req.filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            diff_text = f"--- /dev/null\n+++ b/{req.filepath}\n@@ -0,0 +1,{len(lines)} @@\n" + "".join(["+" + l for l in lines])

        # Compute additions & deletions
        additions = len([l for l in diff_text.split("\n") if l.startswith("+") and not l.startswith("+++")])
        deletions = len([l for l in diff_text.split("\n") if l.startswith("-") and not l.startswith("---")])

        return {
            "filepath": req.filepath or "all",
            "diff": diff_text,
            "additions": additions,
            "deletions": deletions
        }
    except Exception as e:
        return {"error": str(e), "diff": "", "additions": 0, "deletions": 0}


@app.post("/api/review/audit")
async def review_audit_endpoint(req: CodeReviewAuditRequest):
    """Runs an automated code review / quality audit using CentralAgentBrain or local rules."""
    try:
        diff_to_review = req.diff_context
        if not diff_to_review and req.filepath:
            proc = subprocess.run(["git", "diff", "--", req.filepath], cwd=os.path.abspath("."), capture_output=True, text=True)
            diff_to_review = proc.stdout
        
        if not diff_to_review:
            # Fallback to recent git diff head
            proc = subprocess.run(["git", "diff", "HEAD~1"], cwd=os.path.abspath("."), capture_output=True, text=True)
            diff_to_review = proc.stdout[:3000] if proc.stdout else "No recent diffs found."

        # Quick structural heuristics + Gemini AI review prompt
        findings = []

        # 1. Structural linter check
        for line in diff_to_review.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                stripped = line[1:].strip()
                if "console.log" in stripped:
                    findings.append({
                        "severity": "info",
                        "title": "Leftover Console Log",
                        "description": f"Found debug log in changes: `{stripped[:80]}`",
                        "suggestion": "Remove console.log before production deployment."
                    })
                if "eval(" in stripped:
                    findings.append({
                        "severity": "critical",
                        "title": "Security: Insecure eval()",
                        "description": "Arbitrary code execution risk with eval().",
                        "suggestion": "Replace eval() with structured parsers."
                    })
                if "TODO" in stripped or "FIXME" in stripped:
                    findings.append({
                        "severity": "warning",
                        "title": "Unresolved Debt / TODO",
                        "description": f"Unaddressed marker: `{stripped[:80]}`",
                        "suggestion": "Track or complete this item before merge."
                    })

        # 2. Query CentralAgentBrain for high-level code quality summary if brain is active
        summary = "Code diff checked. No critical syntax flaws detected."
        try:
            brain = CentralAgentBrain()
            prompt = (
                f"Perform a concise professional senior software engineer code review on this git diff:\n\n"
                f"```diff\n{diff_to_review[:2000]}\n```\n\n"
                f"Format as: 1) Summary (2 sentences), 2) Potential Risks or Bugs, 3) Architecture & Cleanliness score (1-10)."
            )
            ai_eval = brain.run(prompt)
            if ai_eval:
                summary = ai_eval
        except Exception as ai_err:
            summary = f"Local rules passed ({len(findings)} notes found). AI review skipped: {ai_err}"

        return {
            "status": "completed",
            "findings": findings,
            "ai_review": summary
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "findings": []}


@app.post("/api/review/test")
def review_test_endpoint():
    """Runs automated unit test suite with pytest."""
    try:
        proc = subprocess.run(
            ["pytest", "--color=no", "-q"],
            cwd=os.path.abspath("."),
            capture_output=True,
            text=True,
            timeout=45
        )
        output = proc.stdout
        if proc.stderr:
            output += "\n" + proc.stderr
        return {
            "output": output,
            "passed": proc.returncode == 0,
            "exit_code": proc.returncode
        }
    except subprocess.TimeoutExpired:
        return {"output": "Tests timed out after 45s.", "passed": False, "exit_code": 124}
    except Exception as e:
        return {"output": f"Test runner error: {str(e)}", "passed": False, "exit_code": 1}



if __name__ == "__main__":
    uvicorn.run("agent_server:app", host="127.0.0.1", port=8765, log_level="info")
