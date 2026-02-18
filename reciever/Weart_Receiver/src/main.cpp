#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "LMU-Wireless";
const char* username = "";
const char* password = "";

WiFiUDP udp;
const unsigned int localPort = 5005;

class GloveController {
  private:
    uint8_t seq;
    uint8_t fingers[5];
    
  public:
    void updateFromPacket(const uint8_t* packet) {
      seq = packet[0];
      for (int i = 0; i < 5; i++) {
        fingers[i] = packet[i + 1];
      }
    }
    
    void logValues() {
      Serial.print("Sequence: ");
      Serial.println(seq);
      
      Serial.print("Finger closures: ");
      for (int i = 0; i < 5; i++) {
        Serial.print(fingers[i]);
        if (i < 4) Serial.print(", ");
      }
      Serial.println();
    }
    
    void controlActuators() {
      // Implement actuator control logic here
      // Can convert closure values (0-255) to motor commands
      // SIMON, or whoever, access the values through the fingers array
    }
};

GloveController glove;

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.begin(ssid, WPA2_AUTH_PEAP, username, username, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  udp.begin(localPort);
  Serial.print("Send packets to: ");
  Serial.print(WiFi.localIP());
  Serial.print(":");
  Serial.println(localPort);
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    Serial.print("Received packet from: ");
    Serial.print(udp.remoteIP());
    Serial.print(":");
    Serial.println(udp.remotePort());

    uint8_t incomingPacket[6];
    int len = udp.read(incomingPacket, 6);
    
    if (len >= 6) {
      glove.updateFromPacket(incomingPacket);
      glove.logValues();
      glove.controlActuators();
    } else {
      Serial.print("Invalid packet size: ");
      Serial.println(len);
    }
  }
}
