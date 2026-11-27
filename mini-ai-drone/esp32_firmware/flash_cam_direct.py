import serial
import time
import os
import sys
import esptool
import esptool.targets.esp32 as esp32
import esptool.cmds as cmds

PORT = '/dev/ttyACM0'
BAUD = 115200

BUILD_DIR = '/home/mullainathan/projects/mini-ai-drone/esp32_firmware/esp32_cam_webserver/.pio/build/esp32cam'
BOOT_APP0 = '/home/mullainathan/.platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin'

BOOTLOADER = os.path.join(BUILD_DIR, 'bootloader.bin')
PARTITIONS = os.path.join(BUILD_DIR, 'partitions.bin')
FIRMWARE   = os.path.join(BUILD_DIR, 'firmware.bin')

for f in [BOOTLOADER, PARTITIONS, FIRMWARE, BOOT_APP0]:
    if not os.path.exists(f):
        print(f"[!] Error: Missing required file: {f}")
        sys.exit(1)

addr_data = [
    (0x1000, BOOTLOADER),
    (0x8000, PARTITIONS),
    (0xe000, BOOT_APP0),
    (0x10000, FIRMWARE),
]

print("==========================================================")
print("  DIRECT ESP32-CAM FIRMWARE FLASHER (VIA S3 BRIDGE)       ")
print("==========================================================")
print(f"[*] Target files verified:")
print(f"    0x01000: {os.path.basename(BOOTLOADER)} ({os.path.getsize(BOOTLOADER)} bytes)")
print(f"    0x08000: {os.path.basename(PARTITIONS)} ({os.path.getsize(PARTITIONS)} bytes)")
print(f"    0x0e000: {os.path.basename(BOOT_APP0)} ({os.path.getsize(BOOT_APP0)} bytes)")
print(f"    0x10000: {os.path.basename(FIRMWARE)} ({os.path.getsize(FIRMWARE)} bytes)")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1.0)
    ser.dtr = False
    ser.rts = False
    time.sleep(1.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
except Exception as e:
    print(f"[!] Failed to open {PORT}: {e}")
    sys.exit(1)

print("\n[*] S3 Transparent Bridge active.")
print("[*] >>> PRESS AND RELEASE THE RST BUTTON ON ESP32-CAM NOW! <<<")

# Wait for camera boot banner (3-minute window)
t_end = time.time() + 180.0
detected = False
buf = b""

while time.time() < t_end:
    if ser.in_waiting:
        chunk = ser.read(ser.in_waiting)
        buf += chunk
        if b"waiting for download" in buf or b"DOWNLOAD_BOOT" in buf:
            print("\n [CAMERA DETECTED] ROM Download Bootloader active!")
            detected = True
            time.sleep(0.2)
            ser.reset_input_buffer()
            break
    time.sleep(0.02)

if not detected:
    print("\n[-] Timeout waiting for RST button press.")
    ser.close()
    sys.exit(1)

print("[*] Synchronizing with ESP32-CAM ROM...")
rom_loader = esp32.ESP32ROM(ser)

try:
    rom_loader.connect(mode='no-reset', attempts=10)
    print(" Sync Established!")
    print(f"    Chip:     {rom_loader.CHIP_NAME}")
    print(f"    MAC:      {rom_loader.read_mac()}")
    
    print("\n[*] Writing flash binaries directly at 115200 baud...")
    cmds.write_flash(
        esp=rom_loader,
        addr_data=addr_data,
        flash_mode='dio',
        flash_freq='40m',
        flash_size='4MB',
        compress=True
    )
    print("\n" + "="*58)
    print(" ESP32-CAM FLASHED SUCCESSFULLY! ")
    print("="*58)
    print("\nNext Steps:")
    print("1. DISCONNECT Pin 3 (IO0) from GND on the camera.")
    print("2. Press the RST button on the camera.")
    print("3. Camera will connect to Wi-Fi: AirFiber-Joh1li_EXT")
except Exception as e:
    print(f"\n[-] Flashing error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ser.close()
