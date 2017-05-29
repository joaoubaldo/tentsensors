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
import cherrypy
import requests

from tentsensord import common
from tentsensord import operations
from tentsensord.utils import child_name_by_id
from tentsensord.utils import json_serial
from tentsensord.httpservices import DeviceWebService
from tentsensord.httpservices import ControlWebService


logic = None


def update_child_state(child_id, value, message=None):
    """ set device value. update timestamp and persist current_state. """
    if message:
        value = message.payload
        child_id = message.child_id

    print('Setting', child_id, 'to', value)

    common.current_state[child_name_by_id(child_id)] = {
        'value': str(value),
        'last_update': datetime.utcnow()
    }

    if 'persist_file' in common.config and common.config['persist_file']:
        with open(common.config['persist_file'], 'w') as f:
            f.write(json.dumps(common.current_state, default=json_serial))


def message_handler(message):
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
    elif command == MessageType.req:
        print("child %s state requested. type: %s" % (message.child_id,
                                                      type_))
        name = child_name_by_id(message.child_id)
        value = common.current_state[name]
        if value == '1':
            operations.turn_on(name)
        elif value == '0':
            operations.turn_off(name)


def load_logic_module():
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


def sighup_handler(signum, frame):
    """ reload configuration file and logic module """
    try:
        common.load_config()
        load_logic_module()
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

    """ load common.config_file """
    common.config_file = sys.argv[1]
    common.load_config()

    """ setup posix signal handling """
    signal.signal(signal.SIGHUP, sighup_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
    print("Registered signal handlers")

    """ set children initial state """
    for device in common.config['child_map'].values():
        update_child_state(device, 0)

    load_logic_module()

    """ open the serial interface and start gw thread """
    common.init_gw_thread(message_handler)
    common.gw_thread.start()
    print("Mysensors gateway started")

    """ give a few seconds for gw to startup """
    print("Sleeping for a few seconds")
    time.sleep(5)

    """ start http interface """
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    cherrypy.tree.mount(DeviceWebService(), '/device', conf)
    cherrypy.tree.mount(ControlWebService(), '/control', conf)
    cherrypy.engine.start()
    print("Started HTTP interface")

    """ run logic while gw is active """
    while common.gw_thread.is_alive():
        if common.logic_enabled:
            logic.run()
        if 'influxdb_uri' in common.config:
            data = ''
            for k, v in common.current_state.items():
                data += "%s,host=localhost value=%s\n" % (k, v['value'])
            url = "%(influxdb_uri)s/write?db=%(influxdb_db)s" % common.config
        time.sleep(common.config['loop_sleep'])

    """ clean up """
    print("Cleaning up")
    cherrypy.engine.stop()


if __name__ == '__main__':
    """ entry point """
    main()
