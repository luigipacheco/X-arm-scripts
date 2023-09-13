/**
* esp32_gripper.ino
*
* open and close a gripper woth osc.
*
* Luis Pacheco
*/

#include "WiFi.h"
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <ESP32Servo.h>

#define RDF_NETWORK

Servo finger;
int servoPin = 13;

WiFiUDP udp;
int port = 55555;

#ifdef RDF_NETWORK
const char* ssid = "RDF_Rapture";
const char* password = "WiFi4RDF*!";
IPAddress static_IP(192, 168, 50, 10);
IPAddress gateway(192, 168, 50, 1);
IPAddress subnet(255, 255, 255, 0);
#else
const char* ssid = "otherSSID";
const char* password = "OTHERPASSWORD";
// Set your Static IP address
IPAddress static_IP(192, 168, 50, 10);
IPAddress gateway(192, 168, 50, 1);
IPAddress subnet(255, 255, 255, 0);
#endif

void setup() {
  Serial.begin(115200);
  finger.attach(servoPin, 500, 2400);
  
  // Configure a Static Address
  if (!WiFi.config(static_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }

  // Connect to the wifi router's network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  // Confirm the Static Address
  Serial.print("ESP32_0 IP Address: ");
  Serial.println(WiFi.localIP());

  // Begin listening on the UDP port
  udp.begin(port);
}

void loop() {
  check_for_OSC_message();
  delay(5);
}

void check_for_OSC_message() {
  OSCMessage msg;
  int size = udp.parsePacket();
  
  if (size > 0) {
    Serial.println("Received OSC Message");
    while (size--) {
      msg.fill(udp.read());
    }
    
    if (!msg.hasError()) {
      char msg_addr[255];
      msg.getAddress(msg_addr);
      Serial.print("MSG_ADDR: ");
      Serial.println(msg_addr);
      String msg_addr_str = String(msg_addr);

      // Handle the message based on address
      if (msg_addr_str.indexOf("/grip") != -1) {
        Serial.println("Gripper closed");
        finger.write(0);
      } else if (msg_addr_str.indexOf("/ungrip") != -1) {
        Serial.println("Gripper open");
        finger.write(180);
      }

      // Print the values for debugging
      for (int i = 0; i < msg.size(); i++) {
        Serial.print("\tVALUE\t");
        Serial.print(msg.getType(i));
        Serial.print(": ");
        
        if (msg.isInt(i)) {
          Serial.println(msg.getInt(i));
        } else if (msg.isFloat(i)) {
          Serial.println(msg.getFloat(i));
        } else if (msg.isDouble(i)) {
          Serial.println(msg.getDouble(i));
        } else if (msg.isString(i)) {
          char my_string[255];
          msg.getString(i, my_string);
          Serial.println(my_string);
        } else if (msg.isBoolean(i)) {
          Serial.println(msg.getBoolean(i));
        } else {
          Serial.println("Unknown data type.");
        }
      }
    } else {
      Serial.println("Error in OSC message");
    }
  }
}