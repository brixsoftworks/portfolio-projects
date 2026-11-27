import serial
import time
import re
import sys

PORT = '/dev/ttyACM0'
BAUD = 115200

print("==========================================================", flush=True)
print("  MONITORING ESP32-CAM BOOT & WI-FI CONNECTION            ", flush=True)
print("==========================================================", flush=True)

def open_port():
    while True:
        try:
            s = serial.Serial()
            s.port = PORT
            s.baudrate = BAUD
            s.timeout = 0.1
            s.dtr = False
            s.rts = False
            s.open()
            time.sleep(1.0)
            s.reset_input_buffer()
            return s
        except Exception:
            time.sleep(0.5)

ser = open_port()
print("[*] Connected! Listening for camera boot & Wi-Fi IP...", flush=True)

t_end = time.time() + 1800.0

while time.time() < t_end:
    try:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode('latin1', errors='replace')
            sys.stdout.write(chunk)
            sys.stdout.flush()
            
            # Check for IP address
            match = re.search(r'http://(\d+\.\d+\.\d+\.\d+)', chunk)
            if match:
                ip = match.group(1)
                print("\n" + "="*58, flush=True)
                print(f"🎉 CAMERA ONLINE AT: http://{ip}", flush=True)
                print(f"🎥 STREAM URL:      http://{ip}:81/stream", flush=True)
                print("="*58, flush=True)
        time.sleep(0.05)
    except (serial.SerialException, OSError):
        try:
            ser.close()
        except Exception:
            pass
        time.sleep(1.0)
        ser = open_port()
        print("[*] Reconnected to serial port. Resuming log...", flush=True)

try:
    ser.close()
except Exception:
    pass
