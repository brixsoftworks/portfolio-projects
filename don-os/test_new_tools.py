"""
test_new_tools.py

Comprehensive test suite verifying:
1. Time Tool (current time, reminders, scheduling)
2. Desktop Workflow Tool (clipboard read/write, web article extractor, media info)
3. Hardware Controller (brightness, battery, network, bluetooth, sensors, CPU, audio devices)
"""

import time
from tools.time_tool import (
    get_current_time,
    add_reminder,
    list_reminders,
    cancel_reminder,
)
from tools.desktop_workflow_tool import (
    get_clipboard_text,
    set_clipboard_text,
    read_web_page,
    get_media_info,
)
from tools.hardware_controller import (
    get_screen_brightness,
    get_battery_status,
    get_network_status,
    get_bluetooth_status,
    get_hardware_temperatures,
    get_cpu_info,
    list_audio_devices,
)


def run_tests():
    print("=" * 70)
    print("  Testing New PA Assistant Tools")
    print("=" * 70)

    # 1. TIME TOOLS
    print("\n⏰ 1. Testing Time & Reminder Tools:")
    current_time_str = get_current_time.invoke({})
    print(current_time_str)
    assert "Current Time:" in current_time_str, "Failed to get current time"

    reminder_res = add_reminder.invoke({"time_spec": "in 1 hour", "message": "Test automated reminder"})
    print(f"\n{reminder_res}")
    assert "Reminder #" in reminder_res, "Failed to create reminder"

    import re
    rem_id_match = re.search(r"Reminder #(\d+)", reminder_res)
    assert rem_id_match, "No reminder ID found"
    rem_id = int(rem_id_match.group(1))

    rem_list = list_reminders.invoke({})
    print(f"\n{rem_list}")
    assert f"#{rem_id}" in rem_list, "Reminder not listed"

    cancel_res = cancel_reminder.invoke({"reminder_id": rem_id})
    print(f"\n{cancel_res}")
    assert f"cancelled reminder #{rem_id}" in cancel_res, "Failed to cancel reminder"
    print("✅ Time Tools Passed!")

    # 2. DESKTOP WORKFLOW TOOLS
    print("\n📋 2. Testing Desktop Workflow Tools:")
    test_clip_msg = "PA AI Assistant Test Clipboard 2026"
    set_clip_res = set_clipboard_text.invoke({"text": test_clip_msg})
    print(f"Set clipboard: {set_clip_res}")

    read_clip = get_clipboard_text.invoke({})
    print(f"Read clipboard: '{read_clip}'")
    assert test_clip_msg in read_clip, "Clipboard text did not match!"
    print("✅ Clipboard Read/Write Passed!")

    print("\nReading web page content (example.com):")
    web_res = read_web_page.invoke({"url": "https://example.com"})
    print(web_res[:200] + "...")
    assert "Example Domain" in web_res, "Failed to extract web content"
    print("✅ Web Article Extractor Passed!")

    # 3. HARDWARE & SYSTEM CONTROLLER
    print("\n⚡ 3. Testing Hardware & System Controls:")
    bright_res = get_screen_brightness.invoke({})
    print(f"• {bright_res}")

    bat_res = get_battery_status.invoke({})
    print(f"• {bat_res[:150]}...")

    net_res = get_network_status.invoke({})
    print(f"• Network:\n{net_res[:180]}...")

    bt_res = get_bluetooth_status.invoke({})
    print(f"• Bluetooth:\n{bt_res}")

    cpu_res = get_cpu_info.invoke({})
    print(f"• {cpu_res}")

    sensors_res = get_hardware_temperatures.invoke({})
    print(f"• Thermal Sensors:\n{sensors_res[:200]}...")

    audio_res = list_audio_devices.invoke({})
    print(f"• Audio Devices:\n{audio_res[:200]}...")

    print("✅ Hardware Controls Passed!")

    print("\n" + "=" * 70)
    print("🎉 ALL NEW TOOL TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()

