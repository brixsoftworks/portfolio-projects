"""Tests for MCP connector management and per-message attachment."""

import asyncio
import json
import tempfile
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

import agent
import agent_server
import tools.mcp_controller as mcp_controller


class MCPConnectorAPITests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="pa-mcp-api-")
        self.config_path = Path(self.temp_dir.name) / "mcp_config.json"
        self.config_path.write_text(
            json.dumps({"mcpServers": {
                "existing": {
                    "command": "python",
                    "args": ["-m", "existing_mcp"],
                    "env": {"ACCESS_TOKEN": "not-returned-to-ui"},
                }
            }}),
            encoding="utf-8",
        )
        self.config_patch = patch.object(mcp_controller, "CONFIG_FILE", self.config_path)
        self.config_patch.start()
        self.client = TestClient(agent_server.app)

    def tearDown(self):
        self.config_patch.stop()
        self.temp_dir.cleanup()

    def test_machine_default_catalog_includes_installed_host_connectors(self):
        default_config_path = Path(mcp_controller.__file__).parent.parent / "mcp_config.json"
        servers = json.loads(default_config_path.read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(len(servers), 20)
        self.assertIn("azure-mcp", servers)
        self.assertTrue(Path(servers["azure-mcp"]["command"]).is_file())
        self.assertEqual(servers["foundry-mcp"]["transport"], "http")
        self.assertEqual(servers["github-copilot-mcp"]["transport"], "http")
        self.assertIn("blender-mcp", servers)
        self.assertIn("craft-photocraft", servers)

    def test_add_list_test_and_remove_connector_without_leaking_environment_values(self):
        listed = self.client.get("/api/mcp/servers")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["servers"][0]["env_keys"], ["ACCESS_TOKEN"])
        self.assertNotIn("not-returned-to-ui", listed.text)

        added = self.client.post("/api/mcp/servers", json={
            "name": "fixture-files",
            "command": "/usr/bin/python3",
            "args": ["-m", "fixture_server"],
            "env": {"FIXTURE_TOKEN": "secret-fixture"},
        })
        self.assertEqual(added.status_code, 200, added.text)
        self.assertEqual(added.json()["status"], "configured")
        self.assertEqual(
            json.loads(self.config_path.read_text(encoding="utf-8"))["mcpServers"]["fixture-files"]["env"],
            {"FIXTURE_TOKEN": "secret-fixture"},
        )

        duplicate = self.client.post("/api/mcp/servers", json={
            "name": "fixture-files",
            "command": "python",
        })
        self.assertEqual(duplicate.status_code, 409)

        with patch.object(
            agent_server,
            "fetch_server_tools_async",
            new=AsyncMock(return_value=[{
                "raw_name": "list_files",
                "description": "List fixture files",
            }]),
        ) as discover:
            tested = self.client.post("/api/mcp/servers/fixture-files/test")
        self.assertEqual(tested.status_code, 200, tested.text)
        self.assertEqual(tested.json()["tools"][0]["name"], "list_files")
        discover.assert_awaited_once()

        removed = self.client.delete("/api/mcp/servers/fixture-files")
        self.assertEqual(removed.status_code, 200)
        self.assertEqual(removed.json()["status"], "removed")
        self.assertNotIn(
            "fixture-files",
            json.loads(self.config_path.read_text(encoding="utf-8"))["mcpServers"],
        )

    def test_adds_remote_http_connector_without_exposing_headers(self):
        added = self.client.post("/api/mcp/servers", json={
            "name": "fixture-remote",
            "transport": "http",
            "url": "https://mcp.example.test/mcp",
            "headers": {
                "Authorization": "Bearer fixture-secret",
                "X-MCP-Toolsets": "default",
            },
        })
        self.assertEqual(added.status_code, 200, added.text)
        listing = self.client.get("/api/mcp/servers")
        self.assertIn("mcp.example.test", listing.text)
        self.assertNotIn("fixture-secret", listing.text)
        saved = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.assertEqual(
            saved["mcpServers"]["fixture-remote"]["transport"],
            "http",
        )
        self.assertEqual(
            saved["mcpServers"]["fixture-remote"]["headers"]["Authorization"],
            "Bearer fixture-secret",
        )

    def test_rejects_invalid_connector_names_and_unconfigured_chat_attachments(self):
        invalid = self.client.post("/api/mcp/servers", json={
            "name": "../outside",
            "command": "python",
        })
        self.assertEqual(invalid.status_code, 400)

        chat = self.client.post("/api/chat", json={
            "prompt": "Use this connector",
            "mcp_servers": ["not-configured"],
        })
        self.assertEqual(chat.status_code, 400)
        self.assertIn("Unknown MCP connector", chat.json()["detail"])


class MCPChatAttachmentTests(unittest.TestCase):
    def _run_with_tool_server(self, target_server):
        executed = []

        class FakeModel:
            def __init__(self):
                self.turn = 0

            def invoke(self, messages):
                self.turn += 1
                if self.turn == 1:
                    system = next(message.content for message in messages if isinstance(message, SystemMessage))
                    self.assert_catalog = "fixture_tool" in system
                    return AIMessage(content="", tool_calls=[{
                        "name": "call_mcp_software_tool",
                        "args": {
                            "server_name": target_server,
                            "tool_name": "fixture_tool",
                            "arguments_json": "{\"value\":\"sample\"}",
                        },
                        "id": "mcp-1",
                        "type": "tool_call",
                    }])
                tool_result = next(message.content for message in messages if isinstance(message, ToolMessage))
                return AIMessage(content=f"Connector result: {tool_result}")

        fake_model = FakeModel()
        brain = agent.CentralAgentBrain.__new__(agent.CentralAgentBrain)
        brain.session_id = "mcp-attachment-test"
        brain.history = []
        brain.bound_models = [("fixture-model", fake_model)]
        mock_call = AsyncMock(return_value="fixture server data")

        async def discover(*args, **kwargs):
            return [{
                "raw_name": "fixture_tool",
                "description": "Reads fixture data",
                "input_schema": {"type": "object", "properties": {"value": {"type": "string"}}},
            }]

        with patch.object(agent, "load_mcp_config_strict", return_value={
            "mcpServers": {"fixture-server": {"command": "fixture-command"}}
        }), patch.object(agent, "fetch_server_tools_async", side_effect=discover), patch.object(
            agent, "call_mcp_tool_async", mock_call
        ), patch.object(agent, "record_chat_turn"):
            result = brain.execute_prompt(
                "Read fixture data",
                mcp_servers=["fixture-server"],
            )
        return result, mock_call, fake_model

    def test_selected_connector_is_discovered_and_used(self):
        result, called, model = self._run_with_tool_server("fixture-server")
        self.assertEqual(result["status"], "success")
        self.assertIn("fixture server data", result["response"])
        self.assertTrue(model.assert_catalog)
        called.assert_awaited_once_with(
            "fixture-server", "fixture_tool", {"value": "sample"}
        )

    def test_unselected_connector_cannot_be_called(self):
        result, called, _ = self._run_with_tool_server("other-server")
        self.assertEqual(result["status"], "success")
        self.assertIn("not attached", result["response"])
        called.assert_not_awaited()

    def test_streamable_http_discovery_and_invocation_use_configured_headers(self):
        class FakeHttpClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

        class FakeSession:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def initialize(self):
                return None

            async def list_tools(self):
                return SimpleNamespace(tools=[SimpleNamespace(
                    name="remote_fixture",
                    description="Fixture remote tool",
                    input_schema={"type": "object"},
                )])

            async def call_tool(self, name, arguments):
                return SimpleNamespace(content=[SimpleNamespace(text=f"{name}:{arguments['value']}")])

        @asynccontextmanager
        async def fake_streamable_http_client(url, http_client=None):
            self.assertEqual(url, "https://mcp.example.test/mcp")
            self.assertIsNotNone(http_client)
            yield object(), object()

        http_config = {
            "type": "http",
            "transport": "http",
            "url": "https://mcp.example.test/mcp",
            "headers": {"Authorization": "Bearer fixture-token"},
        }
        with patch.object(mcp_controller.httpx2, "AsyncClient", return_value=FakeHttpClient()), patch.object(
            mcp_controller, "streamable_http_client", side_effect=fake_streamable_http_client
        ), patch.object(mcp_controller, "ClientSession", return_value=FakeSession()) as session_factory:
            discovered = asyncio.run(
                mcp_controller.fetch_server_tools_async("fixture-remote", http_config, raise_on_error=True)
            )
            called = asyncio.run(
                mcp_controller.call_mcp_tool_async(http_config, "remote_fixture", {"value": "works"})
            )

        self.assertEqual(discovered[0]["raw_name"], "remote_fixture")
        self.assertEqual(called, "remote_fixture:works")
        self.assertEqual(session_factory.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
