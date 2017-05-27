from datetime import datetime
import time

import mysensors.mysensors as mysensors
from mysensors.const_20 import MessageType
from mysensors.const_20 import Presentation
from mysensors.const_20 import SetReq
from mysensors.const_20 import Internal


child_map = {
'hum1': 10,
'hum2': 11,
'temp1': 12,
'temp2': 13,
'Resistor': 14,
'Fan': 15,
'Extractor': 16,
'LED': 17,
'HPS': 18,
'Humidifier': 19
}

current_state = {}


logic = {
"day_start": 16,
"day_end": 6,
"target_night_temp": 20,
"target_day_temp": 25,
}

def child_name_by_id(id_):
    for k, v in child_map.items():
        if v == int(id_):
            return k
    return None


def event(message):
    gw = message.gateway
    command = message.type
    type = message.sub_type

    if command == MessageType.presentation:
        if message.child_id == 255:
            pass
        else:
            print("%s is a %s" % (child_name_by_id(message.child_id), message.sub_type))
    elif command == MessageType.set:
        current_state[child_name_by_id(message.child_id)] = message.payload
        print(current_state)


GATEWAY = mysensors.SerialGateway('/dev/ttyUSB0', event, protocol_version='1.5', baud=115200)
GATEWAY.start()

""" give a few seconds for gw to startup """
time.sleep(5)


def is_day(now=None):
    if not now:
        now = datetime.now()
    start = 16
    end = 6
    if start > end:
        return now >= now.replace(hour=start) or now < now.replace(hour=end)
    else:
        return now >= now.replace(hour=start) and now < now.replace(hour=end)


while True:
    if is_day():
        print("day logic...")
    else:
        print("night logic...")
    time.sleep(2)
