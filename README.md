# TentSensors

## Description

TentSensors is the software component of a smart greenhouse
project. The code relies on MySensors library and implements a local
Gateway and Sensor Node.

## Requirements

* Arduino Nano (328p)
* MySensors 2.1.1
* DHT lib for Arduino
* platformio

## Arduino code

Inside **extra/arduino/tentsensors/** there's the Arduino code ready to be
used with platformio.

### Building and uploading
  platformio init  
  platformio run  
  platformio run -t upload

### Monitor device
  platformio device monitor -b 115200

## Service

### Run tests
  nosetests  
  pylint tentsensord  
  pep8 tentsensord

### Test locally
  python setup.py develop

### Install

#### influxdb
  > curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE tentsensord"  
  > curl -i -XPOST http://localhost:8086/query --data-urlencode 'q=CREATE RETENTION POLICY "default" ON "tentsensord" DURATION 30d REPLICATION 1 DEFAULT'

#### service
  python setup.py install
