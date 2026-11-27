from tools.web_search import search, web_search
from tools.bash_tool import bash_tool
from tools.tts_speaker import speak_text
from tools.file_tool import (
    read_file,
    write_file,
    append_file,
    list_directory,
    delete_file,
)
from tools.desktop_controller import (
    launch_app,
    close_app,
    open_url,
    set_volume,
    get_volume,
    take_screenshot,
)
from tools.mcp_controller import (
    list_mcp_servers,
    get_all_mcp_tools,
    load_mcp_config,
)
from tools.time_tool import (
    get_current_time,
    set_timer,
    add_reminder,
    list_reminders,
    cancel_reminder,
)
from tools.desktop_workflow_tool import (
    get_clipboard_text,
    set_clipboard_text,
    read_web_page,
    get_media_info,
    download_media,
)
from tools.hardware_controller import (
    get_screen_brightness,
    set_screen_brightness,
    get_battery_status,
    get_network_status,
    scan_wifi_networks,
    toggle_wifi,
    get_bluetooth_status,
    toggle_bluetooth,
    get_hardware_temperatures,
    get_cpu_info,
    list_audio_devices,
    toggle_microphone_mute,
    lock_desktop_screen,
)
from tools.memory_tool import (
    remember,
    recall,
    forget,
    list_all_memories,
    save_note,
    search_notes,
)
from tools.acp_controller import (
    list_acp_servers,
    call_acp_agent,
    add_acp_server,
    load_acp_config,
)
