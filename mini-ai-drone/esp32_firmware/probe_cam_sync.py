import serial
import time
import struct
import sys

print("==========================================================")
print("  ESP32-CAM ROM BOOTLOADER SYNC TEST (BOARD IS WARM!)     ")
print("==========================================================")

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.08)
    ser.dtr = False
    ser.rts = False
    time.sleep(1.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
except Exception as e:
    print(f"[!] Serial Error: {e}")
    sys.exit(1)

# Espressif SLIP SYNC frame
sync_payload = b'\x07\x07\x12\x20' + 32 * b'\x55'
slip_frame = b'\xc0\x00\x08' + struct.pack('<H', len(sync_payload)) + b'\x00\x00\x00\x00' + sync_payload + b'\xc0'

print("[*] Transmitting SLIP SYNC frames for 15 seconds...")
print("[*] PRESS THE RST BUTTON ON THE ESP32-CAM ONCE NOW!")

t_end = time.time() + 15.0
attempt = 0
synced = False

while time.time() < t_end:
    attempt += 1
    ser.write(slip_frame)
    time.sleep(0.06)
    
    if ser.in_waiting:
        resp = ser.read(ser.in_waiting)
        print(f"\n>>> [RESPONSE RECEIVED: {len(resp)} bytes] <<<", flush=True)
        print(f"  HEX:  {resp.hex()}", flush=True)
        try:
            print(f"  TEXT: {resp.decode('utf-8', errors='replace')}", flush=True)
        except:
            pass
        if b'\xc0' in resp:
            print("\n [SUCCESS] ESP32-CAM SYNCED WITH BOOTLOADER! ", flush=True)
            synced = True
            break
    else:
        print(f"[*] Attempt {attempt:02d}: Waiting for CAM reply... (Press RST)", end='\r', flush=True)

ser.close()
if not synced:
    print("\n[-] No sync response captured in 15 seconds.")
