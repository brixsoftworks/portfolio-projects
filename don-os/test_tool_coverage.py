"""Isolated coverage tests for every native agent tool and multi-step reasoning loops."""

import importlib
import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import agent
import tools.acp_controller as acp_controller
import tools.desktop_controller as desktop_controller
import tools.desktop_workflow_tool as desktop_workflow
import tools.file_tool as file_tool
import tools.hardware_controller as hardware
import tools.memory_tool as memory
import tools.mcp_controller as mcp_controller
import tools.time_tool as time_tool
import tools.tts_speaker as tts
web_search_module = importlib.import_module("tools.web_search")
from langchain_core.messages import AIMessage, ToolMessage
from tools import speak_text


class ToolCoverageTests(unittest.TestCase):
    def test_every_core_tool_individually(self):
        """Invoke all 47 agent tools with harmless inputs or isolated external effects."""
        self.assertEqual(len(agent.CORE_TOOLS), len(agent.TOOL_MAP))
        self.assertEqual(len(agent.CORE_TOOLS), 47)

        with tempfile.TemporaryDirectory(prefix="pa-tool-tests-") as temp_dir:
            root = Path(temp_dir)
            fixture = root / "fixture.txt"
            fixture.write_text("isolated tool fixture", encoding="utf-8")
            inputs = {
                "web_search": {"query": "safe test query"},
                "bash_tool": {"command": "printf safe-tool-test"},
                "read_file": {"file_path": str(fixture)},
                "write_file": {"file_path": str(root / "write.txt"), "content": "test"},
                "append_file": {"file_path": str(root / "append.txt"), "content": "test"},
                "list_directory": {"directory_path": str(root)},
                "delete_file": {"file_path": str(fixture)},
                "get_current_time": {},
                "set_timer": {"seconds": 1, "label": "isolated test"},
                "add_reminder": {"time_spec": "in 1 hour", "message": "isolated test"},
                "list_reminders": {},
                "cancel_reminder": {"reminder_id": -1},
                "get_clipboard_text": {},
                "set_clipboard_text": {"text": "isolated clipboard test"},
                "read_web_page": {"url": "https://example.invalid"},
                "get_media_info": {"url": "https://example.invalid/video"},
                "download_media": {
                    "url": "https://example.invalid/video",
                    "output_dir": str(root / "downloads"),
                },
                "get_screen_brightness": {},
                "set_screen_brightness": {"percentage": 50},
                "get_battery_status": {},
                "get_network_status": {},
                "scan_wifi_networks": {},
                "toggle_wifi": {"enable": True},
                "get_bluetooth_status": {},
                "toggle_bluetooth": {"enable": True},
                "get_hardware_temperatures": {},
                "get_cpu_info": {},
                "list_audio_devices": {},
                "toggle_microphone_mute": {"mute": True},
                "lock_desktop_screen": {},
                "launch_app": {"app_name": "test-app", "app_args": ""},
                "close_app": {"process_name": "test-app"},
                "open_url": {"url": "https://example.invalid"},
                "set_volume": {"percentage": 25},
                "get_volume": {},
                "take_screenshot": {"filename": str(root / "screenshot.png")},
                "remember": {"key": "isolated_test", "information": "fixture"},
                "recall": {"query": "isolated_test"},
                "forget": {"key": "isolated_test"},
                "list_all_memories": {},
                "save_note": {"title": "Isolated test", "content": "fixture"},
                "search_notes": {"query": "Isolated test"},
                "call_mcp_software_tool": {
                    "server_name": "mock-server",
                    "tool_name": "mock_tool",
                    "arguments_json": "{}",
                },
                "list_available_mcp_servers": {},
                "list_acp_servers": {},
                "call_acp_agent": {"server_name": "mock-agent", "task": "safe test"},
                "add_acp_server": {
                    "name": "isolated-test",
                    "command": "mock-command",
                    "description": "isolated test",
                },
            }
            self.assertEqual(set(inputs), set(agent.TOOL_MAP))

            results = {}
            with ExitStack() as mocks:
                mocks.enter_context(patch.object(
                    web_search_module,
                    "search",
                    SimpleNamespace(run=Mock(return_value="mock search result")),
                ))
                mocks.enter_context(patch.object(file_tool, "request_delete_permission", return_value=True))

                class NoStartThread:
                    def __init__(self, *args, **kwargs):
                        self.args = args

                    def start(self):
                        return None

                mocks.enter_context(patch.object(time_tool.threading, "Thread", NoStartThread))
                reminders_db = str(root / "reminders.db")
                mocks.enter_context(patch.object(time_tool, "DB_DIR", temp_dir))
                mocks.enter_context(patch.object(time_tool, "DB_PATH", reminders_db))
                time_tool._init_db()

                memory_db = str(root / "memory.db")
                mocks.enter_context(patch.object(memory, "DB_DIR", temp_dir))
                mocks.enter_context(patch.object(memory, "DB_PATH", memory_db))
                memory._init_memory_db()

                mocks.enter_context(patch.object(desktop_workflow.shutil, "which", return_value="/mock/bin"))
                def fake_subprocess_run(command, *args, **kwargs):
                    parts = command if isinstance(command, list) else [command]
                    executable = os.path.basename(str(parts[0]).split()[0])
                    if "--dump-single-json" in parts:
                        return SimpleNamespace(
                            returncode=0,
                            stdout=json.dumps({
                                "title": "Fixture video",
                                "uploader": "Test",
                                "duration": 90,
                                "view_count": "N/A",
                            }),
                            stderr="",
                        )
                    if executable == "grim":
                        Path(parts[-1]).write_bytes(b"mock screenshot")
                    outputs = {
                        "brightnessctl": "Device 'test-backlight'\nCurrent brightness: 5 (50%)",
                        "upower": "",
                        "nmcli": "mock connection",
                        "ip": "lo UP 127.0.0.1/8",
                        "bluetoothctl": "Powered: yes",
                        "sensors": "Mock temperature: +40.0 C",
                        "lscpu": "Model name: Test CPU\nCPU(s): 1",
                        "pactl": "Volume: front-left: 65536 / 100% / 0.00 dB\nMute: no",
                        "loginctl": "",
                    }
                    if executable == "pactl":
                        return SimpleNamespace(
                            returncode=0,
                            stdout=outputs[executable],
                            stderr="",
                        )
                    if executable == "wl-paste":
                        return SimpleNamespace(returncode=0, stdout="fixture clipboard", stderr="")
                    return SimpleNamespace(
                        returncode=0,
                        stdout=outputs.get(executable, "mock"),
                        stderr="",
                    )

                mocks.enter_context(patch.object(
                    desktop_workflow.subprocess, "run", side_effect=fake_subprocess_run
                ))
                mocks.enter_context(patch.object(
                    desktop_workflow.subprocess,
                    "Popen",
                    return_value=SimpleNamespace(communicate=Mock(return_value=(None, None))),
                ))

                class FakePage:
                    def __enter__(self):
                        return self

                    def __exit__(self, *args):
                        return False

                    def read(self):
                        return b"<html><head><title>Fixture</title></head><body><main><p>This is a sufficiently long fixture paragraph for extraction.</p></main></body></html>"

                mocks.enter_context(patch.object(desktop_workflow.urllib.request, "urlopen", return_value=FakePage()))
                mocks.enter_context(patch.object(desktop_workflow.os.path, "exists", return_value=True))
                mocks.enter_context(patch.object(hardware.shutil, "which", return_value="/mock/bin"))

                mocks.enter_context(patch.object(desktop_controller.shutil, "which", return_value="/mock/app"))
                mocks.enter_context(patch.object(desktop_controller.subprocess, "Popen"))
                mocks.enter_context(patch.object(desktop_controller, "DEFAULT_SCREENSHOT_DIR", str(root)))

                async_mcp = AsyncMock(return_value="mock MCP result")
                mocks.enter_context(patch.object(agent, "call_mcp_tool_async", async_mcp))
                mocks.enter_context(patch.object(agent, "load_mcp_config", return_value={
                    "mcpServers": {"isolated-test-server": {"command": "mock"}}
                }))
                mocks.enter_context(patch.object(acp_controller, "_run_sync", return_value="mock ACP result"))
                acp_config_file = root / "acp_config.json"
                acp_config_file.write_text(json.dumps({
                    "acpServers": {
                        "mock-agent": {
                            "command": "mock-command",
                            "args": [],
                            "description": "isolated test",
                        }
                    }
                }), encoding="utf-8")
                mocks.enter_context(patch.object(acp_controller, "CONFIG_FILE", acp_config_file))

                for name, arguments in inputs.items():
                    with self.subTest(tool=name):
                        result = agent.TOOL_MAP[name].invoke(arguments)
                        self.assertIsInstance(result, str)
                        self.assertTrue(result.strip(), f"{name} returned an empty result")
                        results[name] = result

            self.assertIn("Title: Fixture video", results["get_media_info"])
            self.assertIn("URL: https://example.invalid/video", results["get_media_info"])
            print(f"\nIndividual tool checks: {len(results)}/{len(inputs)} passed")
            for name in inputs:
                print(f"  PASS {name}")

    def test_memory_and_reminder_lifecycles_in_temporary_databases(self):
        with tempfile.TemporaryDirectory(prefix="pa-tool-lifecycle-") as temp_dir:
            with patch.object(memory, "DB_DIR", temp_dir), patch.object(
                memory, "DB_PATH", str(Path(temp_dir) / "memory.db")
            ):
                memory._init_memory_db()
                self.assertIn("Successfully saved", memory.remember.invoke({
                    "key": "lifecycle", "information": "fixture", "category": "test"
                }))
                self.assertIn("lifecycle", memory.recall.invoke({"query": "fixture"}))
                self.assertIn("Successfully saved note", memory.save_note.invoke({
                    "title": "Lifecycle", "content": "fixture note"
                }))
                self.assertIn("Lifecycle", memory.search_notes.invoke({"query": "fixture"}))
                self.assertIn("Successfully deleted", memory.forget.invoke({"key": "lifecycle"}))

            reminders_db = str(Path(temp_dir) / "reminders.db")
            with patch.object(time_tool, "DB_DIR", temp_dir), patch.object(time_tool, "DB_PATH", reminders_db):
                time_tool._init_db()
                added = time_tool.add_reminder.invoke({
                    "time_spec": "in 1 hour", "message": "isolated lifecycle"
                })
                self.assertIn("Reminder #", added)
                reminder_id = int(added.split("#", 1)[1].split()[0])
                self.assertIn(f"#{reminder_id}", time_tool.list_reminders.invoke({}))
                self.assertIn("Successfully cancelled", time_tool.cancel_reminder.invoke({
                    "reminder_id": reminder_id
                }))

    def test_dynamic_mcp_discovery_uses_configured_server_list(self):
        with patch.object(mcp_controller, "load_mcp_config", return_value={
            "mcpServers": {"mock-server": {"command": "not-executed", "args": []}}
        }), patch.object(mcp_controller, "fetch_server_tools_async", new_callable=AsyncMock) as fetch:
            fetch.return_value = [{
                "raw_name": "fixture_tool",
                "name": "mock-server__fixture_tool",
                "description": "Isolated fixture",
                "config": {"command": "not-executed", "args": []},
            }]
            discovered = mcp_controller.get_all_mcp_tools()
        self.assertEqual([item.name for item in discovered], ["mock-server__fixture_tool"])
        fetch.assert_awaited_once()

    def test_multi_step_tool_call_loop_and_synthesis(self):
        executed = []

        class TestTool:
            def __init__(self, name, func):
                self.name = name
                self.func = func

            def invoke(self, args):
                executed.append(self.name)
                return self.func(args)

        class LoopModel:
            def __init__(self):
                self.calls = 0

            def invoke(self, messages):
                self.calls += 1
                if self.calls == 1:
                    return AIMessage(content="", tool_calls=[{
                        "name": "fixture_read", "args": {}, "id": "read-1", "type": "tool_call"
                    }])
                if self.calls == 2:
                    previous = next(message.content for message in messages if isinstance(message, ToolMessage))
                    return AIMessage(content="", tool_calls=[{
                        "name": "fixture_transform",
                        "args": {"value": previous},
                        "id": "transform-1",
                        "type": "tool_call",
                    }])
                transformed = next(
                    message.content for message in messages
                    if isinstance(message, ToolMessage) and message.tool_call_id == "transform-1"
                )
                return AIMessage(content=f"Verified final result: {transformed}")

        model = LoopModel()
        brain = agent.CentralAgentBrain.__new__(agent.CentralAgentBrain)
        brain.session_id = "isolated-loop"
        brain.history = []
        brain.bound_models = [("fixture-model", model)]
        progress = []
        replacements = {
            "fixture_read": TestTool("fixture_read", lambda args: "raw fixture"),
            "fixture_transform": TestTool("fixture_transform", lambda args: args["value"].upper()),
        }
        with patch.dict(agent.TOOL_MAP, replacements), patch.object(agent, "record_chat_turn"):
            result = brain.execute_prompt("Run the isolated verification loop.", progress_callback=progress.append)

        self.assertEqual(result["status"], "success")
        self.assertEqual(executed, ["fixture_read", "fixture_transform"])
        self.assertIn("Verified final result: RAW FIXTURE", result["response"])
        self.assertEqual(len(result["tool_calls_executed"]), 2)
        self.assertTrue(any("Running fixture_read" in item for item in progress))
        self.assertTrue(any("Running fixture_transform" in item for item in progress))
        self.assertEqual(model.calls, 3)
        print("\nAdvanced loop: 2 dependent tools, 3 model turns, final synthesis passed")

    def test_speech_tool_receives_complete_cleaned_response(self):
        long_text = " ".join(f"Sentence {index} is included." for index in range(30))
        cleaned = tts.clean_speech_text(long_text)
        self.assertGreater(len(cleaned), 280)
        with patch.object(tts, "stop_current_speech"), patch.object(
            tts, "_stream_audio_to_player", new_callable=AsyncMock
        ) as playback:
            speak_text(long_text)
        spoken = playback.call_args.args[0]
        self.assertEqual(spoken, cleaned)
        self.assertTrue(spoken.endswith("included."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
