import serial
import time
import struct
import sys

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.05)
    ser.dtr = False
    ser.rts = False
    time.sleep(0.5)
    ser.reset_input_buffer()
except Exception as e:
    print(f"Error opening port: {e}")
    sys.exit(1)

sync_payload = b'\x07\x07\x12\x20' + 32 * b'\x55'
slip_frame = b'\xc0\x00\x08' + struct.pack('<H', len(sync_payload)) + b'\x00\x00\x00\x00' + sync_payload + b'\xc0'

print("==========================================================", flush=True)
print("  TRANSPARENT FLASH BRIDGE LISTENING (10-MINUTE WINDOW)    ", flush=True)
print("==========================================================", flush=True)
print("[*] Probing and listening for 10 minutes (600s)...", flush=True)

t_end = time.time() + 600.0
synced = False
total_bytes = 0

while time.time() < t_end:
    ser.write(slip_frame)
    time.sleep(0.06)
    if ser.in_waiting:
        resp = ser.read(ser.in_waiting)
        total_bytes += len(resp)
        print(f"\n [DATA FROM ESP32-CAM: {len(resp)} bytes] ", flush=True)
        print(f"  HEX:  {resp.hex()}", flush=True)
        print(f"  TEXT: {resp.decode('latin1', errors='replace')}", flush=True)
        if b'\xc0' in resp:
            print("\n [SUCCESS] ESP32-CAM BOOTLOADER SYNC ESTABLISHED! ", flush=True)
            synced = True
            break

ser.close()
if not synced and total_bytes == 0:
    print("\n[-] No serial response captured.", flush=True)
