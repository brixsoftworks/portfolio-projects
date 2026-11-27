#include <Arduino.h>

HardwareSerial CamSerial(1);

const int CAM_RX_PIN = 18; // S3 RX <- CAM TX (Pin 7)
const int CAM_TX_PIN = 17; // S3 TX -> CAM RX (Pin 6)

void setup() {
    Serial.begin(115200);
    CamSerial.begin(115200, SERIAL_8N1, CAM_RX_PIN, CAM_TX_PIN);
}

void loop() {
    // 1. Laptop -> Camera
    while (Serial.available()) {
        CamSerial.write(Serial.read());
    }
    
    // 2. Camera -> Laptop
    while (CamSerial.available()) {
        Serial.write(CamSerial.read());
    }
}
