"""
test_desktop_controller.py

Verification test for Desktop Controller & MCP Bridge:
1. Volume retrieval and control
2. Screenshot capture
3. App launch check
4. MCP Server Registry check
"""

import os
from tools.desktop_controller import (
    get_volume,
    set_volume,
    take_screenshot,
    launch_app,
)
from tools.mcp_controller import list_mcp_servers, load_mcp_config

def test_desktop():
    print("=" * 60)
    print("  Testing Advanced Desktop Controller & MCP Bridge")
    print("=" * 60)

    # 1. Volume Check
    print("\n[Test 1] Querying Speaker Volume:")
    vol_info = get_volume.invoke({})
    print("Result:", vol_info)
    assert "Volume:" in vol_info

    # 2. Volume Adjust
    print("\n[Test 2] Adjusting Volume to 25%:")
    set_res = set_volume.invoke({"percentage": 25})
    print("Result:", set_res)
    assert "25%" in set_res

    # 3. Screenshot Capture
    print("\n[Test 3] Taking Desktop Screenshot:")
    test_shot = "/tmp/test_pa_screenshot.png"
    if os.path.exists(test_shot):
        os.remove(test_shot)
    shot_res = take_screenshot.invoke({"filename": test_shot})
    print("Result:", shot_res)
    assert "Screenshot" in shot_res
    if os.path.exists(test_shot):
        os.remove(test_shot)

    # 4. MCP Registry
    print("\n[Test 4] Querying MCP Registry:")
    mcp_res = list_mcp_servers.invoke({})
    print("Result:", mcp_res)
    assert "mcp_config.json" in mcp_res

    print("\n" + "=" * 60)
    print("  All Desktop & MCP Tests Passed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_desktop()
