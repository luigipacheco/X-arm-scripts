/**
* esp32_osc_neopixel_matrix_controller.ino
*
* Changes a Neopixel matrix based on incoming
* OSC values. Code adapted to actuate servo to 
* open and close a rubber gripper.
*
* Madeline Gannon | ATONATON
* Includes changes by Luis Pacheco & Nathan Pothuganti
* April 2023
* https://atonaton.com
*/

#include "WiFi.h"
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>
#include <Adafruit_NeoPixel.h>
#include <ESP32Servo.h>
#define LED_PIN 32
#define LED_COUNT 32

// #define HOME_NETWORK

Servo finger;
int servoPin = 13;
Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

WiFiUDP udp;
int port = 55555;

// const char* ssid = "WHH";
// const char* password = "benderisgreat";
// Set your Static IP address
// IPAddress static_IP(192, 168, 1, 10);
// IPAddress gateway(192, 168, 1, 1);
// IPAddress subnet(255, 255, 255, 0);

// home network 192.168.0.23
#ifdef HOME_NETWORK
const char* ssid = "NETGEAR94";
const char* password = "wideprairie401";
IPAddress static_IP(192, 168, 0, 10);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);
#else
const char* ssid = "WHH";
const char* password = "benderisgreat";
// Set your Static IP address
IPAddress static_IP(192, 168, 1, 10);
IPAddress gateway(192, 168, 1, 1);
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

  // Intialize Neopixel Matrix
  pixels.begin();
  pixels.show();
  pixels.setBrightness(50);
}

void loop() {
  check_for_OSC_message();
  delay(5);
}


void on_message_draw(OSCMessage& msg) {
  if (msg.isString(0)) {
    pixels.clear();
    pixels.show();
  } else {
    int pixel_data_size = msg.size();
    for (int i = 0; i < pixel_data_size; i += 5) {  // we increment by 5 as each pixel has 5 values
      int pixel = msg.getInt(i);
      int r = msg.getInt(i + 1);
      int g = msg.getInt(i + 2);
      int b = msg.getInt(i + 3);
      int w = msg.getInt(i + 4);
      uint32_t color = pixels.Color(r, g, b, w);
      pixels.setPixelColor(pixel, color);
    }
    pixels.show();
  }
}

void on_message_fill(OSCMessage& msg) {
  if (!msg.isString(0)) {
    int r = msg.getInt(0);
    int g = msg.getInt(1);
    int b = msg.getInt(2);
    int w = msg.getInt(3);
    uint32_t color = pixels.Color(r, g, b, w);
    for (int i = 0; i < LED_COUNT; i++) {
      pixels.setPixelColor(i, color);
    }
    pixels.show();
  }
}

void on_message_clear(OSCMessage& msg) {
  pixels.clear();
  pixels.show();
}

void on_message_gh(OSCMessage& msg) {
  if (msg.isString(0)) {
    char my_string[255];
    msg.getString(0, my_string);

    // Split the string into RGB components
    String str = String(my_string);
    int idx1 = str.indexOf(",");
    int idx2 = str.lastIndexOf(",");
    int r = str.substring(0, idx1).toInt();
    int g = str.substring(idx1+1, idx2).toInt();
    int b = str.substring(idx2+1).toInt();

    uint32_t color = pixels.Color(r, g, b);

    for (int i = 0; i < LED_COUNT; i++) {
      pixels.setPixelColor(i, color);
    }
    pixels.show();

    // Print the values for debugging
    Serial.println("Received RGB values: ");
    Serial.println(r);
    Serial.println(g);
    Serial.println(b);
  }
}

void check_for_OSC_message() {
  OSCMessage msg;
  int size = udp.parsePacket();
  if (size > 0) {
    while (size--) {
      msg.fill(udp.read());
    }
    if (!msg.hasError()) {
      // Get the message address
      char msg_addr[255];
      msg.getAddress(msg_addr);
      Serial.print("MSG_ADDR: ");
      Serial.println(msg_addr);
      String msg_addr_str = String(msg_addr);

      // if "/address" is in msg_addr
      if (msg_addr_str.indexOf("/draw") != -1) {
        on_message_draw(msg);
      } else if(msg_addr_str.indexOf("/fill") != -1) {
        on_message_fill(msg);
      } else if(msg_addr_str.indexOf("/clear") != -1) {
        on_message_clear(msg);
      }
      else if(msg_addr_str.indexOf("/0/GH") != -1) {
        on_message_gh(msg);
      }
      else if(msg_addr_str.indexOf("/grip") != -1) {
        finger.write(0);
      }
      else if(msg_addr_str.indexOf("/ungrip") != -1) {
        finger.write(180);
      }
      

      // Example of how to parse the message
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
    }
  }
}