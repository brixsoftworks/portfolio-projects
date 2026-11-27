import serial
import time
import sys

print("==================================================")
print("  LONG-WINDOW CAM MONITOR ON S3 PIN 18 (2 MINS)   ")
print("==================================================")

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
    ser.dtr = False
    ser.rts = False
    time.sleep(0.5)
    ser.reset_input_buffer()
except Exception as e:
    print(f"[!] Error opening port: {e}")
    sys.exit(1)

print("[*] Port active! Waiting for ANY signal from ESP32-CAM...")
print("[*] Press the RST button on the camera whenever ready.")

t_end = time.time() + 120.0
total_bytes = 0

while time.time() < t_end:
    if ser.in_waiting:
        chunk = ser.read(ser.in_waiting)
        total_bytes += len(chunk)
        print(f"\n>>> [CAM PACKET RECEIVED: {len(chunk)} bytes] <<<", flush=True)
        print(f"  HEX:  {chunk.hex()}", flush=True)
        try:
            print(f"  TEXT: {chunk.decode('utf-8', errors='replace')}", flush=True)
        except Exception as e:
            print(f"  ERR:  {e}", flush=True)
    time.sleep(0.05)

ser.close()
print(f"\n[*] Monitor finished. Total bytes: {total_bytes}")
