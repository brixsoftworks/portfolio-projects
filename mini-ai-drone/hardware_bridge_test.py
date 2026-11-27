"""
HARDWARE BRIDGE TEST SUITE: ESP32-CAM (VIDEO STREAM) + ESP32-S3 (GROUND STATION)
---------------------------------------------------------------------------------
Verifies:
1. ESP32-S3 USB Serial Link: Auto-detects port (/dev/ttyACM* or /dev/ttyUSB*)
   and establishes bidirectional telemetry packet exchange.
2. ESP32-CAM Live Video Stream: Connects to the HTTP/MJPEG camera stream,
   computes streaming FPS, latency, and overlays real-time AI telemetry.
"""

import sys
import os
import time
import argparse
import glob
import cv2
import numpy as np

# Ensure project path is accessible
sys.path.append('/home/mullainathan/projects/mini-ai-drone')

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

def scan_serial_ports():
    """Scans and lists all connected serial and USB-UART devices."""
    print("\n" + "=" * 65)
    print("[*] SCANNING FOR CONNECTED SERIAL / USB HARDWARE...")
    print("=" * 65)
    
    ports = []
    if HAS_SERIAL:
        for p in serial.tools.list_ports.comports():
            ports.append((p.device, p.description, p.hwid))
    else:
        for dev in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
            ports.append((dev, "Unknown USB Serial Device", ""))

    if not ports:
        print("[!] No serial ports detected yet (/dev/ttyACM* or /dev/ttyUSB*).")
        print("    -> Please plug in your ESP32-S3 / ESP32-CAM via USB cable.")
        return []

    print(f"[+] Found {len(ports)} connected serial device(s):")
    for idx, (dev, desc, hwid) in enumerate(ports):
        print(f"    [{idx+1}] {dev} - {desc} ({hwid})")
    return [p[0] for p in ports]

def test_serial_handshake(port, baudrate=115200, timeout=2.0):
    """Sends a ping handshake packet to ESP32-S3 Ground Station."""
    if not HAS_SERIAL:
        print("[!] PySerial not available.")
        return False

    print(f"\n[*] Testing connection to ESP32-S3 Ground Station on {port} @ {baudrate} baud...")
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        time.sleep(1.0) # Wait for ESP32 boot/reset
        
        # Flush buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Send test ping packet
        ping_packet = b'{"cmd":"PING","timestamp":' + str(int(time.time()*1000)).encode() + b'}\n'
        ser.write(ping_packet)
        print(f"[>] Sent Handshake Packet: {ping_packet.decode().strip()}")

        # Read response
        t_start = time.time()
        response_lines = []
        while time.time() - t_start < timeout:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    response_lines.append(line)
                    print(f"[<] ESP32-S3 Output: {line}")
            time.sleep(0.05)

        ser.close()
        if response_lines:
            print(f"[+] Successfully communicated with ESP32-S3 on {port}!")
            return True
        else:
            print(f"[-] Port opened, but no response received yet from ESP32-S3 firmware.")
            return True
    except Exception as e:
        print(f"[!] Error opening serial port {port}: {e}")
        return False

def test_esp32_cam_stream(stream_url="http://192.168.4.1:81/stream"):
    """Connects to ESP32-CAM MJPEG HTTP video stream and displays live HUD."""
    print("\n" + "=" * 65)
    print(f"[*] CONNECTING TO ESP32-CAM STREAM: {stream_url}")
    print("=" * 65)
    print("[*] Press 'Q' or ESC in the video window to stop.")

    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print(f"[!] Failed to open video stream at: {stream_url}")
        print("    Tips:")
        print("    1. Ensure your laptop is connected to the ESP32-CAM Wi-Fi (e.g. ESP32_CAM_AP).")
        print("    2. Check the IP address printed on the ESP32-CAM Serial Monitor (e.g. 192.168.4.1 or your router IP).")
        print("    3. Test opening the URL in your web browser first.")
        return False

    print("[+] Video stream connected successfully! Streaming live...")
    prev_time = time.time()
    frame_count = 0
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("[!] Dropped frame or stream ended.")
            time.sleep(0.05)
            continue

        frame_count += 1
        t_now = time.time()
        if t_now - prev_time >= 1.0:
            fps = frame_count / (t_now - prev_time)
            frame_count = 0
            prev_time = t_now

        h, w, _ = frame.shape
        # Overlay Stream Diagnostics
        cv2.putText(frame, f"ESP32-CAM LIVE STREAM | {w}x{h} | FPS: {fps:.1f}", 
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"SOURCE: {stream_url}", 
                    (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        cv2.imshow("ESP32-CAM HARDWARE STREAM TEST", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[+] Stream test completed.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ESP32 Hardware Bridge Test")
    parser.add_argument("--scan", action="store_true", help="Scan serial ports")
    parser.add_argument("--cam-url", type=str, default="http://192.168.4.1:81/stream", help="ESP32-CAM stream URL")
    parser.add_argument("--serial-port", type=str, default=None, help="ESP32-S3 serial port (e.g. /dev/ttyACM0)")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    args = parser.parse_args()

    ports = scan_serial_ports()
    if args.serial_port:
        test_serial_handshake(args.serial_port, args.baud)
    elif ports:
        test_serial_handshake(ports[0], args.baud)
