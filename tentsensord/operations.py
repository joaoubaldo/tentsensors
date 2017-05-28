from datetime import datetime

from tentsensord import common

def last_update(device):
    if device in common.current_state:
        return common.current_state[device]['last_update']
    return None

def device_value(device):
    if device in common.current_state:
        return common.current_state[device]['value']
    return None

def turn_on(device):
    common.gw_thread.set_child_value(0, common.config['child_map'][device], 2, 1)

def turn_off(device):
    common.gw_thread.set_child_value(0, common.config['child_map'][device], 2, 0)

def toggle(device):
    value = device_value(device)
    if value and value == '1':
        turn_off(device)
    elif value and value == '0':
        turn_on(device)
