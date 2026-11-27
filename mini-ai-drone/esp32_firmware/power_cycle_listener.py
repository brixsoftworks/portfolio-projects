import serial
import time
import sys

print("==========================================================")
print("  LIVE ESP32-CAM POWER-ON LISTENER (S3 BRIDGE ACTIVE)     ")
print("==========================================================")

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.05)
    ser.dtr = False
    ser.rts = False
    # Wait 2 seconds for S3 bridge to boot up
    time.sleep(2.0)
    ser.reset_input_buffer()
except Exception as e:
    print(f"[!] Error: {e}")
    sys.exit(1)

print("[*] S3 Bridge is 100% READY and listening on Pin 18!")
print("[*] Monitoring for 60 seconds...")

t_end = time.time() + 60.0
total = 0

while time.time() < t_end:
    if ser.in_waiting:
        data = ser.read(ser.in_waiting)
        total += len(data)
        print(f"\n>>> [CAM DATA DETECTED! {len(data)} BYTES] <<<", flush=True)
        print(f"  HEX:  {data.hex()}", flush=True)
        try:
            print(f"  TEXT: {data.decode('utf-8', errors='replace')}", flush=True)
        except Exception as e:
            print(f"  ERR:  {e}", flush=True)
    time.sleep(0.02)

ser.close()
print(f"\n[*] Finished. Total bytes: {total}")
