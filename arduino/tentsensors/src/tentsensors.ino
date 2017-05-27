/*
Title: TentSensors 2
Author: Joao Coutinho <me joaoubaldo.com>
Git: https://github.com/joaoubaldo/tentsensors

Description: TentSensors is the software component of a smart greenhouse
project. The code relies on MySensors library and implements a local
Gateway and Sensor Node.
*/

#define MY_GATEWAY_SERIAL

#include <SPI.h>
#include <MySensors.h>
#include <DHT.h>

#include "version.h"

/* IDs */
#define CHILD_ID_HUM 10
#define CHILD_ID_HUM2 11
#define CHILD_ID_TEMP 12
#define CHILD_ID_TEMP2 13
#define CHILD_ID_RELAY1 14
#define CHILD_ID_RELAY2 15
#define CHILD_ID_RELAY3 16 
#define CHILD_ID_LED 17
#define CHILD_ID_RELAY4 18
#define CHILD_ID_RELAY5 19

/* Pins */
#define HUMIDITY_SENSOR_DIGITAL_PIN 4
#define HUMIDITY_SENSOR_DIGITAL_PIN2 3
#define LED_PIN 5
#define RELAY1_PIN 9
#define RELAY2_PIN 7
#define RELAY3_PIN 10
#define RELAY4_PIN 6
#define RELAY5_PIN 11

DHT dht;
DHT dht2;
boolean metric = true;

/* MyMessages */
MyMessage msgHum(CHILD_ID_HUM, V_HUM);
MyMessage msgHum2(CHILD_ID_HUM2, V_HUM);
MyMessage msgTemp(CHILD_ID_TEMP, V_TEMP);
MyMessage msgTemp2(CHILD_ID_TEMP2, V_TEMP);
MyMessage msgRelay1(CHILD_ID_RELAY1, V_STATUS);
MyMessage msgRelay2(CHILD_ID_RELAY2, V_STATUS);
MyMessage msgRelay3(CHILD_ID_RELAY3, V_STATUS);
MyMessage msgRelay4(CHILD_ID_RELAY4, V_STATUS);
MyMessage msgRelay5(CHILD_ID_RELAY5, V_STATUS);
MyMessage msgLed(CHILD_ID_LED, V_STATUS);

/* Control variables */
unsigned long dhtTimer[2] = {0, 0};  // used to control read frequency
unsigned long resetInterval = 7200000;
unsigned long lastStateRefresh = 0;
float lastTemp[2];
float lastHum[2];
MyMessage * humMsgs[2] = {&msgHum, &msgHum2};
MyMessage * tempMsgs[2] = {&msgTemp, &msgTemp2};
DHT * dhts[2] = {&dht, &dht2};
unsigned long stateRefreshInterval = 10000;
unsigned int dhtReadInterval = 5000;
int sendFailCount = 0;
int lastSendFailCount = 0;
unsigned long lastSendFailTimer = 0;

void setupInitialPinsState() {
  pinMode(RELAY1_PIN, OUTPUT);
  digitalWrite(RELAY1_PIN, HIGH);
  pinMode(RELAY2_PIN, OUTPUT);
  digitalWrite(RELAY2_PIN, HIGH);
  pinMode(RELAY3_PIN, OUTPUT);
  digitalWrite(RELAY3_PIN, HIGH);
  pinMode(RELAY4_PIN, OUTPUT);
  digitalWrite(RELAY4_PIN, HIGH);
  pinMode(RELAY5_PIN, OUTPUT);
  digitalWrite(RELAY5_PIN, HIGH);

 
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void requestAllStates() {
  //if ((millis() - lastStateRefresh) >= stateRefreshInterval) {
    request(CHILD_ID_RELAY1, V_STATUS);
    request(CHILD_ID_RELAY2, V_STATUS);
    request(CHILD_ID_RELAY3, V_STATUS);
    request(CHILD_ID_RELAY4, V_STATUS);
    request(CHILD_ID_RELAY5, V_STATUS);
    request(CHILD_ID_LED, V_STATUS);
    lastStateRefresh = millis();
  //}
}

void setup() {
  dht.setup(HUMIDITY_SENSOR_DIGITAL_PIN);
  dht2.setup(HUMIDITY_SENSOR_DIGITAL_PIN2);

  setupInitialPinsState();
  wait(2000);
  requestAllStates();
}

void presentation() {
  sendSketchInfo("TentSensors", VERSION);
  wait(200);
  present(CHILD_ID_HUM, S_HUM);
  wait(200);
  present(CHILD_ID_TEMP, S_TEMP);
  wait(200);
  present(CHILD_ID_HUM2, S_HUM);
  wait(200);
  present(CHILD_ID_TEMP2, S_TEMP);
  wait(200);
  present(CHILD_ID_RELAY1, S_LIGHT);
  wait(200);
  present(CHILD_ID_RELAY2, S_LIGHT);
  wait(200);
  present(CHILD_ID_RELAY3, S_LIGHT);
  wait(200);
  present(CHILD_ID_RELAY4, S_LIGHT);
  wait(200);
  present(CHILD_ID_RELAY5, S_LIGHT);
  wait(200);
  present(CHILD_ID_LED, S_LIGHT);
  wait(200);
}

void loop() {
  readHumTemp();
}

void receive(const MyMessage & message) {
  if (message.type == V_STATUS && message.sensor == CHILD_ID_RELAY1) {
    digitalWrite(RELAY1_PIN, !message.getBool());
    send(msgRelay1.set(message.getBool() ? 1:0));
  } else if (message.type == V_STATUS && message.sensor == CHILD_ID_RELAY2) {
    digitalWrite(RELAY2_PIN, !message.getBool());
    send(msgRelay2.set(message.getBool() ? 1:0));
  } else if (message.type == V_STATUS && message.sensor == CHILD_ID_RELAY3) {
    digitalWrite(RELAY3_PIN, !message.getBool());
    send(msgRelay3.set(message.getBool() ? 1:0));
  } else if (message.type == V_STATUS && message.sensor == CHILD_ID_RELAY4) {
    digitalWrite(RELAY4_PIN, !message.getBool());
    send(msgRelay4.set(message.getBool() ? 1:0));
  } else if (message.type == V_STATUS && message.sensor == CHILD_ID_RELAY5) {
    digitalWrite(RELAY5_PIN, !message.getBool());
    send(msgRelay5.set(message.getBool() ? 1:0));
  } else if (message.type == V_STATUS && message.sensor == CHILD_ID_LED) {
    digitalWrite(LED_PIN, message.getBool());
    send(msgLed.set(message.getBool() ? 1:0));
  }
}

void readHumTemp() {
  for (int i = 0; i < 2; i++) {
    if ((millis() - dhtTimer[i]) >= dhtReadInterval) {
      float temperature = dhts[i]->getTemperature();
      float humidity = dhts[i]->getHumidity();  // this wont actually read again from sensor
      if (isnan(temperature)) {
      } else {
        lastTemp[i] = temperature;
        if (!metric) {
          temperature = dhts[i]->toFahrenheit(temperature);
        }
        if (!send(tempMsgs[i]->set(temperature, 1)))
          sendFailCount++;
      }

      if (isnan(humidity)) {
      } else {
          lastHum[i] = humidity;

          wait(100);
          if (!send(humMsgs[i]->set(humidity, 1)))
            sendFailCount++;
      }

      dhtTimer[i] = millis();
    }
  }
}
