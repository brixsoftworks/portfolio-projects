import serial
import time
import os
import sys
import struct
import esptool.loader
import esptool.targets.esp32 as esp32
import esptool.cmds as cmds

# Increase esptool timeouts for transparent hardware bridge
esptool.loader.SYNC_TIMEOUT = 1.0
esptool.loader.DEFAULT_TIMEOUT = 5.0

PORT = '/dev/ttyACM0'
BAUD = 115200

BUILD_DIR = '/home/mullainathan/projects/mini-ai-drone/esp32_firmware/esp32_cam_webserver/.pio/build/esp32cam'
BOOT_APP0 = '/home/mullainathan/.platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin'

BOOTLOADER = os.path.join(BUILD_DIR, 'bootloader.bin')
PARTITIONS = os.path.join(BUILD_DIR, 'partitions.bin')
FIRMWARE   = os.path.join(BUILD_DIR, 'firmware.bin')

for f in [BOOTLOADER, PARTITIONS, FIRMWARE, BOOT_APP0]:
    if not os.path.exists(f):
        print(f"[!] Missing file: {f}")
        sys.exit(1)

addr_data = [
    (0x1000, BOOTLOADER),
    (0x8000, PARTITIONS),
    (0xe000, BOOT_APP0),
    (0x10000, FIRMWARE),
]

print("==========================================================")
print("  AUTOMATIC CONTINUOUS ESP32-CAM FLASHER                  ")
print("==========================================================")
print("[*] Binaries ready for 4MB Flash (AI-Thinker OV2640)")

def get_serial():
    while True:
        try:
            s = serial.Serial()
            s.port = PORT
            s.baudrate = BAUD
            s.timeout = 0.1
            s.dtr = False
            s.rts = False
            s.open()
            time.sleep(1.5)
            s.reset_input_buffer()
            return s
        except Exception as e:
            time.sleep(0.5)

ser = get_serial()

# Espressif SLIP SYNC frame
sync_payload = b'\x07\x07\x12\x20' + 32 * b'\x55'
slip_frame = b'\xc0\x00\x08' + struct.pack('<H', len(sync_payload)) + b'\x00\x00\x00\x00' + sync_payload + b'\xc0'

print("[*] Probing for camera boot... (2-hour listening window)", flush=True)
print("[*] >>> POWER CYCLE: UNPLUG & REPLUG THE RED (3.3V) WIRE AT THE CAMERA! <<<", flush=True)

t_end = time.time() + 7200.0
synced = False

while time.time() < t_end:
    try:
        ser.write(slip_frame)
        time.sleep(0.06)
        
        if ser.in_waiting:
            resp = ser.read(ser.in_waiting)
            print(f"\n[RAW] Incoming ({len(resp)} bytes): {resp}", flush=True)
            
            # If the S3 board itself rebooted, ignore it
            if b'esp32s3' in resp:
                print("[-] (Ignored S3 board reboot text - waiting for camera...)", flush=True)
                continue

            # If camera booted in normal mode (IO0 was high)
            if b'boot:0x13' in resp or (b'ets Jul' in resp and b'SPI_FAST_FLASH_BOOT' in resp):
                print("\n[WARN] [CAMERA DETECTED IN NORMAL BOOT] Camera is alive and powered, but IO0 is NOT grounded!", flush=True)
                print(" Please ensure Brown wire (IO0) is firmly connected to GND, then power-cycle again!\n", flush=True)
                continue

            # If boot text is seen, note it and KEEP SENDING SLIP FRAMES!
            if any(marker in resp for marker in [b'waiting for download', b'DOWNLOAD_BOOT']):
                print("[*] Bootloader detected! Sending SLIP sync frames to lock baud rate...", flush=True)
                continue

            # Only break when camera sends actual SLIP SYNC ACK (\xc0\x01\x08)
            if b'\xc0\x01\x08' in resp or (b'\xc0' in resp and len(resp) >= 14):
                print(f"\n [SLIP SYNC CONFIRMED FROM CAMERA] Captured sync ACK ({len(resp)} bytes)", flush=True)
                time.sleep(0.1)
                ser.reset_input_buffer()
                synced = True
                break
    except (serial.SerialException, OSError) as port_err:
        print(f"\n[!] Port disconnected/reset ({port_err}). Re-opening {PORT}...", flush=True)
        try:
            ser.close()
        except Exception:
            pass
        time.sleep(1.0)
        ser = get_serial()
        print("[*] Port re-opened! Resuming probe...", flush=True)

if not synced:
    print("\n[-] No camera response captured.")
    ser.close()
    sys.exit(1)

print("\n" + "="*58)
print(" SYNC CONFIRMED! FLASHING IN PROGRESS...            ")
print("   DO NOT TOUCH ANY WIRES OR BUTTONS!                 ")
print("="*58)

try:
    rom = esp32.ESP32ROM(ser)
    rom.connect(mode='no-reset', attempts=30)
    print(f"[*] Connected: {rom.CHIP_NAME} (MAC: {rom.read_mac()})")
    
    print("[*] Uploading flasher stub for maximum transfer speed...")
    try:
        loader = rom.run_stub()
        print("    Flasher stub running!")
    except Exception as stub_err:
        print(f"    (Direct ROM fallback: {stub_err})")
        loader = rom

    print("[*] Writing flash at 115200 baud (Bootloader + App + Partitions)...")
    cmds.write_flash(
        esp=loader,
        addr_data=addr_data,
        flash_mode='dio',
        flash_freq='40m',
        flash_size='4MB',
        compress=True
    )
    
    print("\n" + "="*58)
    print(" ESP32-CAM FIRMWARE FLASH COMPLETE! ")
    print("="*58)
    print("\nFINAL STEPS:")
    print("1. UNPLUG / REMOVE Pin 3 (IO0) from GND on the camera.")
    print("2. CLICK the RST button once on the camera.")
    print("3. Camera will boot and connect to Wi-Fi: AirFiber-Joh1li_EXT")
except Exception as e:
    print(f"\n[-] Flash error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ser.close()
