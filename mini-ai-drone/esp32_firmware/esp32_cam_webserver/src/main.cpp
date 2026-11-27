#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include "esp_wifi.h"

// ===========================
// Select camera model in board_config.h
// ===========================
#include "board_config.h"

// ===========================
// Enter your WiFi credentials
// ===========================
const char *ssid = "AirFiber-Joh1li_EXT";
const char *password = "ec4hahVeeNge5chi";

void startCameraServer();
void setupLedFlash();

void setup() {
  // Turn ON onboard red LED (GPIO 33, active LOW) to show board is running!
  pinMode(33, OUTPUT);
  digitalWrite(33, LOW);

  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
  Serial.println("[*] ESP32-CAM Booting - Red LED ON");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA; // 640x480 (4x higher resolution than QVGA)
  config.pixel_format = PIXFORMAT_RGB565; // Native support for GC2145 (RHYX M21-45)
  config.grab_mode = CAMERA_GRAB_LATEST; // Real-time zero-lag frame grabbing
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10; // High clarity JPEG
  config.fb_count = 2; // Double buffering in PSRAM for smooth 30 FPS

  // camera init with fallback
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[!] RGB565 init failed (0x%x), trying YUV422...\n", err);
    config.pixel_format = PIXFORMAT_YUV422;
    err = esp_camera_init(&config);
  }
  if (err != ESP_OK) {
    Serial.printf("[!] YUV422 init failed (0x%x), trying JPEG...\n", err);
    config.pixel_format = PIXFORMAT_JPEG;
    err = esp_camera_init(&config);
  }
  if (err != ESP_OK) {
    Serial.printf("[ERROR] Camera init failed: 0x%x\n", err);
    // Fast blink LED to indicate sensor error
    while (true) {
      digitalWrite(33, !digitalRead(33));
      delay(150);
    }
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    s->set_framesize(s, FRAMESIZE_VGA);
    s->set_brightness(s, 1);
    s->set_contrast(s, 1);
    s->set_saturation(s, 1);
    if (s->id.PID == OV3660_PID) {
      s->set_vflip(s, 1);
      s->set_brightness(s, 1);
      s->set_saturation(s, -2);
    }
  }

#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_19_5dBm); // Boost transmission power to maximum (19.5 dBm = 100mW)
  esp_wifi_set_ps(WIFI_PS_NONE); // Disable all power saving for ultra-low latency

  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(33, !digitalRead(33)); // Blink LED while connecting
    delay(400);
    Serial.print(".");
  }
  digitalWrite(33, LOW); // Solid LED once connected!

  Serial.println("");
  Serial.println("WiFi connected!");

  startCameraServer();

  Serial.println("\n==================================================");
  Serial.printf(" CAMERA READY! Web UI: http://%s\n", WiFi.localIP().toString().c_str());
  Serial.printf(" LIVE STREAM:         http://%s:81/stream\n", WiFi.localIP().toString().c_str());
  Serial.println("==================================================");
}

void loop() {
  delay(10000);
}
