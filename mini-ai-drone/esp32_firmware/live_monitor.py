import serial
import time
import sys

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
    ser.dtr = False
    ser.rts = False
    time.sleep(0.5)
except Exception as e:
    print(f"Error opening port: {e}")
    sys.exit(1)

print("[*] LIVE HARDWARE WATCHDOG (15-MINUTE WINDOW)...", flush=True)
t_end = time.time() + 900.0

while time.time() < t_end:
    if ser.in_waiting:
        line = ser.read(ser.in_waiting).decode('latin1', errors='replace')
        print(line, end='', flush=True)
    time.sleep(0.05)

ser.close()
