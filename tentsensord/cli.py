from datetime import datetime
from datetime import timedelta
import importlib.machinery
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

from tentsensord import common
from tentsensord import operations

logic = None

def child_name_by_id(id_):
    """ get device name by id """
    for k, v in common.config['child_map'].items():
        if v == int(id_):
            return k
    return None

def update_child_state(child_id, value, message=None):
    """ set device value. update timestamp and persist current_state. """
    if message:
        value = message.payload
        child_id = message.child_id

    print('Setting', child_id, 'to', value)

    common.current_state[child_name_by_id(child_id)] = {
        'value': str(value),
        'last_update': datetime.now()
    }

    if 'persist_file' in common.config and common.config['persist_file']:
        with open(common.config['persist_file'], 'w') as f:
            f.write(json.dumps(common.current_state, default=json_serial))

def event(message):
    """ mysensors event handler """
    gw = message.gateway
    command = message.type
    type_ = message.sub_type

    if command == MessageType.presentation:
        if message.child_id == 255:
            pass
        else:
            print("%s is a %s" % (child_name_by_id(message.child_id),
                                  message.sub_type))
    elif command == MessageType.set:
        update_child_state(None, None, message)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def load_logic():
    """ load or reload logic module from file path. """
    global logic
    try:
        logic = importlib.machinery.SourceFileLoader(
                'logic',
                common.config['logic_script']).load_module()
    except:
        if common.gw_thread:
            common.gw_thread.stop()
        raise

def load_config(config_dict=None):
    """ load config file. if config_dict is not None, its contents are used
    instead of reading file common.config_file """

    """ TODO: protect against changes to some attributes """
    if not config_dict and len(common.config_file) > 0:
        common.config = json.load(open(common.config_file, 'r'))
    elif config_dict:
        common.config = config_dict

def sighup_handler(signum, frame):
    """ reload configuration file and logic module """
    try:
        load_config()
        load_logic()
        print('SIGHUP: Reloading config from', common.config_file)
    except Exception:
        common.gw_thread.stop()
        raise

def sigterm_handler(signum, frame):
    print('SIGTERM: stopping...')
    common.gw_thread.stop()

def main(config_dict=None):
    if len(sys.argv) != 2:
        print("Usage: %s <config file>" % (sys.argv[0],))
        sys.exit(2)

    common.config_file = sys.argv[1]
    load_config()

    """ setup posix signal handling """
    signal.signal(signal.SIGHUP, sighup_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    """ set children initial state """
    for device in common.config['child_map'].values():
        update_child_state(device, 0)

    load_logic()

    """ open the serial interface """
    common.gw_thread = mysensors.SerialGateway(
            common.config["device"], event, protocol_version='1.5',
            baud=common.config["baud_rate"])
    common.gw_thread.start()

    """ give a few seconds for gw to startup """
    time.sleep(5)

    while common.gw_thread.is_alive():
        logic.run()
        time.sleep(common.config['loop_sleep'])


if __name__ == '__main__':
    """ entry point """
    main()
