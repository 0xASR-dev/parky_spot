#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi credentials
const char* ssid = "Open-source";
const char* password = "00000000";

// Flask server URL
const char* serverURL = "http://192.168.8.21:5000/update-sensor-data"; // Replace with Flask server IP

const int sensorPins[] = {5, 19, 18, 23};
const int sensorCount = sizeof(sensorPins) / sizeof(sensorPins[0]);

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < sensorCount; i++) {
    pinMode(sensorPins[i], INPUT);
  }

  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  String jsonData = "{";
  for (int i = 0; i < sensorCount; i++) {
    int sensorState = digitalRead(sensorPins[i]);
    jsonData += "\"sensor" + String(i + 1) + "\":" + String(sensorState);
    if (i < sensorCount - 1) jsonData += ",";
  }
  jsonData += "}";

  sendDataToFlask(jsonData);
  delay(5000); // Send data every 5 seconds
}

void sendDataToFlask(String jsonData) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.print("Error in sending POST request: ");
      Serial.println(http.errorToString(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("Wi-Fi Disconnected");
  }
}
