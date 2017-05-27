from datetime import datetime
from datetime import timedelta
import time
import json
import sys
import os
import signal

import mysensors.mysensors as mysensors
from mysensors import Message
from mysensors.const_20 import MessageType
from mysensors.const_20 import Presentation
from mysensors.const_20 import SetReq
from mysensors.const_20 import Internal

current_state = {}
config_file = ''
config = {}
gw_thread = None


def child_name_by_id(id_):
    for k, v in config['child_map'].items():
        if v == int(id_):
            return k
    return None


def is_day(now=None):
    if not now:
        now = datetime.now()

    start = config['day_start']
    end = config['day_end']

    if start > end:
        return now >= now.replace(hour=start) or now < now.replace(hour=end)
    else:
        return now >= now.replace(hour=start) and now < now.replace(hour=end)


def update_child_state(child_id, value, message=None):
    global current_state

    if message:
        value = message.payload
        child_id = message.child_id

    print('Setting', child_id, 'to', value)

    current_state[child_name_by_id(child_id)] = {
        'value': str(value),
        'last_update': datetime.now()
    }

def last_update(device):
    if device in current_state:
        return current_state[device]['last_update']
    return None

def device_value(device):
    if device in current_state:
        return current_state[device]['value']
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
        update_child_state(None, None, message)


def turn_on(gw, device):
    gw.set_child_value(0, config['child_map'][device], 2, 1)


def turn_off(gw, device):
    gw.set_child_value(0, config['child_map'][device], 2, 0)

def toggle(gw, device):
    if device_value(device) and device_value(device) == '1':
        turn_off(gw, device)
    elif device_value(device) and device_value(device) == '0':
        turn_on(gw, device)


def day_logic(gw):
    now = datetime.now()
    if not last_update('Extractor') or (now - last_update('Extractor')) >= timedelta(seconds=5):
        toggle(gw, 'Extractor')


def night_logic(gw):
    pass


def main():
    global gw_thread

    gw_thread = mysensors.SerialGateway(config["device"], event, protocol_version='1.5', baud=config["baud_rate"])
    gw_thread.start()
    
    """ give a few seconds for gw to startup """
    time.sleep(5)

    while gw_thread.is_alive():
        if is_day():
            day_logic(gw_thread)
        else:
            night_logic(gw_thread)
        time.sleep(config['loop_sleep'])


def sighup_handler(signum, frame):
    global config, config_file
    try:
        """ TODO: protect against changes to some attributes """
        config = json.load(open(config_file, 'r'))
        print('SIGHUP: Reloading config from', config_file)
    except Exception:
        gw_thread.stop()
        raise

def sigterm_handler(signum, frame):
    print('SIGTERM: stopping...')
    gw_thread.stop()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: %s <config file>" % (sys.argv[0],))
        sys.exit(2)

    config_file = sys.argv[1]
    config = json.load(open(config_file, 'r'))

    for device in config['child_map'].values():
        update_child_state(device, 0)

    signal.signal(signal.SIGHUP, sighup_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
    
    main()
