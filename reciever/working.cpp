#include <Arduino.h>
#include <WiFi.h>

const char* ssid = "LMU-Wireless";
const char* username = "name"; // Replace with your actual username
const char* password = "password";

void setup() {
  Serial.begin(115200);
  delay(1000);
  WiFi.begin(ssid, WPA2_AUTH_PEAP, username, username, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Your main code here
}