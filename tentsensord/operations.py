from datetime import datetime

from tentsensord import common


def last_update(device):
    """ return device's last update datetime. None if device doesn't exist """
    if device in common.current_state:
        return common.current_state[device]['last_update']
    return None


def device_value(device):
    """ return current device value. None if device doesn't exist """
    if device in common.current_state:
        return common.current_state[device]['value']
    return None


def turn_on(device):
    """ use the gateway to turn the device on """
    if device_value(device) == '1':
        return
    print("turn on", device)
    common.gw_thread.set_child_value(
        0, common.config['child_map'][device], 2, 1)


def turn_off(device):
    """ use the gateway to turn the device off """
    if device_value(device) == '0':
        return
    print("turn off", device)
    common.gw_thread.set_child_value(
        0, common.config['child_map'][device], 2, 0)


def toggle(device):
    """ use the gateway to toggle the device state """
    value = device_value(device)
    if value and value == '1':
        turn_off(device)
    elif value and value == '0':
        turn_on(device)
