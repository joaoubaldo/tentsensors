import json

import mysensors.mysensors as mysensors

current_state = {}

config_file = ''

config = {}

gw_thread = None

logic_enabled = True

def init_gw_thread(event_handler):
    global gw_thread
    gw_thread = mysensors.SerialGateway(
        config["device"], event_handler, protocol_version='1.5',
        baud=config["baud_rate"])


def load_config(config_dict=None):
    """ load config file. if config_dict is not None, its contents are used
    instead of reading file common.config_file """

    global config
    if not config_dict and len(config_file) > 0:
        config = json.load(open(config_file, 'r'))
    elif config_dict:
        config = config_dict
