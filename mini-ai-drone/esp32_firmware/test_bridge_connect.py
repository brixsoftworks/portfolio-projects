import serial
import time
import esptool.targets.esp32 as esp32

print("==========================================================")
print("  CONNECTING TO ESP32-CAM VIA S3 BRIDGE WITH ZERO-RESET   ")
print("==========================================================")

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)
ser.dtr = False
ser.rts = False
time.sleep(1.2)
ser.reset_input_buffer()
ser.reset_output_buffer()

print("[*] S3 Bridge stable. Creating ESP32ROM loader...")
loader = esp32.ESP32ROM(ser)

print("[*] Attempting connect (mode='no-reset', attempts=20)...")
print("[*] If not syncing, tap the RST button on the ESP32-CAM now!")

try:
    loader.connect(mode='no-reset', attempts=20)
    print(" CONNECTED TO ESP32-CAM CHIP! ")
    print(f"Chip Name:    {loader.CHIP_NAME}")
    print(f"Features:     {loader.get_chip_features()}")
    print(f"Crystal Freq: {loader.get_crystal_freq()} MHz")
    print(f"MAC Address:  {loader.read_mac()}")
except Exception as e:
    print(f"[-] Connect failed: {e}")

ser.close()
