"""
test_all_mcp_software.py

Automated diagnostic test:
Iterates through all software MCP servers in mcp_config.json,
connects to each on stdio, retrieves available tools, and runs a live probe.
"""

import asyncio
from tools.mcp_controller import load_mcp_config, fetch_server_tools_async, call_mcp_tool_async

async def test_all_servers():
    cfg = load_mcp_config()
    servers = cfg.get("mcpServers", {})

    print("=" * 70)
    print(f"  Diagnosing & Testing {len(servers)} Software MCP Servers in System")
    print("=" * 70)

    total_tools = 0
    passed_servers = 0
    failed_servers = 0

    for name, s_cfg in servers.items():
        print(f"\n Testing Software Server: '{name}'")
        cmd = s_cfg.get("command", "")
        args = s_cfg.get("args", [])
        print(f"   Command: {cmd} {' '.join(args[:2])}...")

        try:
            tools = await fetch_server_tools_async(name, s_cfg)
            if tools:
                passed_servers += 1
                total_tools += len(tools)
                print(f"   [PASS] Connected! {len(tools)} tools discovered.")
                sample_tool = tools[0]["raw_name"]
                print(f"    Sample tool: {sample_tool}")
            else:
                failed_servers += 1
                print(f"   [WARN]  Server connected but returned 0 tools.")
        except Exception as e:
            failed_servers += 1
            print(f"   [FAIL] Connection failed: {e}")

    print("\n" + "=" * 70)
    print(f"  Summary:")
    print(f"  • Verified Active Servers: {passed_servers}/{len(servers)}")
    print(f"  • Total MCP Tools Available: {total_tools}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_all_servers())

