/*
Title: TentSensors
Author: Joao Coutinho <me joaoubaldo.com>
Git: https://github.com/joaoubaldo/tentsensors
Description: TentSensors is the software component of a smart greenhouse project.
This code relies on MySensors project and it implements a single node with the following childs:

3x relays
1x led
2x DHT temperature & humidity sensors
*/

#include <SPI.h>

#include <MySensor.h>
#include <DHT.h>

#define VERSION "2.1"

/* IDs */
#define CHILD_ID_HUM 10
#define CHILD_ID_HUM2 11
#define CHILD_ID_TEMP 12
#define CHILD_ID_TEMP2 13
#define CHILD_ID_RELAY1 14
#define CHILD_ID_RELAY2 15
#define CHILD_ID_RELAY3 16
#define CHILD_ID_LED 17

/* Pins */
#define HUMIDITY_SENSOR_DIGITAL_PIN 3
#define HUMIDITY_SENSOR_DIGITAL_PIN2 4
#define LED_PIN 5
#define RELAY1_PIN 6
#define RELAY2_PIN 7
#define RELAY3_PIN 8

MySensor gw;
DHT dht;
DHT dht2;
boolean metric = true;

/* MyMessages */
MyMessage msgHum(CHILD_ID_HUM, V_HUM);
MyMessage msgHum2(CHILD_ID_HUM2, V_HUM);
MyMessage msgTemp(CHILD_ID_TEMP, V_TEMP);
MyMessage msgTemp2(CHILD_ID_TEMP2, V_TEMP);
MyMessage msgRelay1(CHILD_ID_RELAY1, V_LIGHT);
MyMessage msgRelay2(CHILD_ID_RELAY2, V_LIGHT);
MyMessage msgRelay3(CHILD_ID_RELAY3, V_LIGHT);
MyMessage msgLed(CHILD_ID_LED, V_LIGHT);

/* Control variables */
unsigned long dhtTimer[2] = {0, 0};  // used to control read frequency
float lastTemp[2];
float lastHum[2];
MyMessage * humMsgs[2] = {&msgHum, &msgHum2};
MyMessage * tempMsgs[2] = {&msgTemp, &msgTemp2};
DHT * dhts[2] = {&dht, &dht2};

void setupInitialPinsState() {
  pinMode(RELAY1_PIN, OUTPUT);
  digitalWrite(RELAY1_PIN, HIGH);
  pinMode(RELAY2_PIN, OUTPUT);
  digitalWrite(RELAY2_PIN, HIGH);
  pinMode(RELAY3_PIN, OUTPUT);
  digitalWrite(RELAY3_PIN, HIGH);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

}

void requestAllStates() {
  /* HACK bellow */
  delay(50);
  gw.request(CHILD_ID_RELAY1, V_LIGHT);
  delay(50);
  gw.process();
  gw.request(CHILD_ID_RELAY2, V_LIGHT);
  delay(50);
  gw.process();
  gw.request(CHILD_ID_RELAY3, V_LIGHT);
  delay(50);
  gw.process();
  gw.request(CHILD_ID_LED, V_LIGHT);
  delay(50);
  gw.process();
}

void setup()
{
  gw.begin(incomingMessage);

  dht.setup(HUMIDITY_SENSOR_DIGITAL_PIN);
  dht2.setup(HUMIDITY_SENSOR_DIGITAL_PIN2);

  gw.sendSketchInfo("TentSensors", VERSION);

  gw.present(CHILD_ID_HUM, S_HUM);
  gw.present(CHILD_ID_TEMP, S_TEMP);
  gw.present(CHILD_ID_HUM2, S_HUM);
  gw.present(CHILD_ID_TEMP2, S_TEMP);
  gw.present(CHILD_ID_RELAY1, S_LIGHT);
  gw.present(CHILD_ID_RELAY2, S_LIGHT);
  gw.present(CHILD_ID_RELAY3, S_LIGHT);
  gw.present(CHILD_ID_LED, S_LIGHT);

  metric = gw.getConfig().isMetric;

  setupInitialPinsState();

  requestAllStates();
}

void loop()
{
  readHumTemp();
  gw.process();
}

void incomingMessage(const MyMessage & message) {
  if (message.type == V_LIGHT && message.sensor == CHILD_ID_RELAY1) {
    digitalWrite(RELAY1_PIN, !message.getBool());
    gw.send(msgRelay1.set(message.getBool() ? 1:0));
  } else if (message.type == V_LIGHT && message.sensor == CHILD_ID_RELAY2) {
    digitalWrite(RELAY2_PIN, !message.getBool());
    gw.send(msgRelay2.set(message.getBool() ? 1:0));
  } else if (message.type == V_LIGHT && message.sensor == CHILD_ID_RELAY3) {
    digitalWrite(RELAY3_PIN, !message.getBool());
    gw.send(msgRelay3.set(message.getBool() ? 1:0));
  } else if (message.type == V_LIGHT && message.sensor == CHILD_ID_LED) {
    digitalWrite(LED_PIN, message.getBool());
    gw.send(msgLed.set(message.getBool() ? 1:0));
  }
}

void readHumTemp() {
  for (int i = 0; i < 2; i++) {
    if ((millis() - dhtTimer[i]) >= dhts[i]->getMinimumSamplingPeriod()) {
      float temperature = dhts[i]->getTemperature();
      if (isnan(temperature)) {
      } else {
        lastTemp[i] = temperature;
        if (!metric) {
          temperature = dhts[i]->toFahrenheit(temperature);
        }
        gw.send(tempMsgs[i]->set(temperature, 1));
      }

      float humidity = dhts[i]->getHumidity();
      if (isnan(humidity)) {
      } else {
          lastHum[i] = humidity;
          gw.send(humMsgs[i]->set(humidity, 1));
      }
      dhtTimer[i] = millis();
    }
  }
}
