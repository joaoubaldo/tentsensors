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
  python setup.py install
