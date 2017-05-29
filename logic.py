from datetime import datetime
from datetime import timedelta

from tentsensord import operations
from tentsensord import common


def time_since_update(device):
    return datetime.utcnow() - common.current_state[device]['last_update']


def turn_on_every_x_for_y(device, x, y):
    """ x, y - seconds """
    time_since_update = time_since_update(device).total_seconds()
    value = common.current_state[device]['value']

    if time_since_update >= x and value == '0':
        print(device," was OFF for ", time_since_update," seconds")
        operations.turn_on(device)
    elif value == '1' and time_since_update >= y:
        print(device, " was ON for ", time_since_update, " seconds")
        operations.turn_off(device)


def is_day(now=None):
    if not now:
        now = datetime.utcnow()

    start = common.config['vars']['day_start']
    end = common.config['vars']['day_end']

    if start > end:
        return now >= now.replace(hour=start) or now < now.replace(hour=end)
    else:
        return now >= now.replace(hour=start) and now < now.replace(hour=end)


def day_logic():
    now = datetime.utcnow()
    if not operations.last_update('Extractor') or \
    (now - operations.last_update('Extractor')) >= timedelta(minutes=30):
        operations.toggle('Extractor')

    if not operations.last_update('Fan') or \
    (now - operations.last_update('Fan')) >= timedelta(minutes=15):
        operations.toggle('Fan')


def night_logic():
    temp1 = float(common.current_state['Temp1']['value'])
    temp2 = float(common.current_state['Temp2']['value'])

    hum1 = float(common.current_state['Hum1']['value'])
    hum2 = float(common.current_state['Hum2']['value'])

    temp = temp1
    hum = hum1

    if abs(temp1-temp2) > 5.0:
        print("Warning: Large difference between temperature sensors")

    if abs(hum1-hum2) > 15.0:
        print("Warning: Large difference between humidity sensors")

    temp_error = common.config['vars']['target_night_temp'] - temp
    if 0.51 <= temp_error <= 9999.0:
        operations.turn_on('Resistor')
        turn_on_every_x_for_y('Extractor', 600, 120)
        operations.turn_off('Fan')
    elif -0.50 <= temp_error <= 0.50:
        turn_on_every_x_for_y('Fan', 1600, 900)
        turn_on_every_x_for_y('Extractor', 600, 120)
        operations.turn_off('Resistor')
    elif -9999.0 <= temp_error <= -0.51:
        operations.turn_on('Extractor')
        turn_on_every_x_for_y('Fan', 1600, 900)
        operations.turn_off('Resistor')


def run():
    if is_day():
        day_logic()
    else:
        night_logic()
