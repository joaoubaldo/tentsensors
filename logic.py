from datetime import datetime
from datetime import timedelta

from tentsensord import operations
from tentsensord import common


def time_since_update(device):
    return datetime.utcnow() - common.current_state[device]['last_update']


def turn_on_every_x_for_y(device, x, y):
    """ x, y - seconds """
    time_since = time_since_update(device).total_seconds()
    value = operations.device_value(device)

    if time_since >= x and value == '0':
        print(device," was OFF for ", time_since," seconds")
        operations.turn_on(device)
    elif value == '1' and time_since >= y:
        print(device, " was ON for ", time_since, " seconds")
        operations.turn_off(device)


def is_day(now=None):
    if not now:
        now = datetime.now()

    start = common.config['vars']['day_start']
    end = common.config['vars']['day_end']

    if start > end:
        return now >= now.replace(hour=start) or now < now.replace(hour=end)
    else:
        return now >= now.replace(hour=start) and now < now.replace(hour=end)


def day_logic():
    operations.turn_on('HPS')
    try:
        temp1 = float(operations.device_value('Temp1'))
        temp2 = float(operations.device_value('Temp2'))

        hum1 = float(operations.device_value('Hum1'))
        hum2 = float(operations.device_value('Hum2'))
    except:
        return

    temp = temp1
    hum = hum1

    if abs(temp1-temp2) > 5.0:
        print("Warning: Large difference between temperature sensors")

    if abs(hum1-hum2) > 15.0:
        print("Warning: Large difference between humidity sensors")

    temp_error = common.config['vars']['target_day_temp'] - temp
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


def night_logic():
    operations.turn_off('HPS')
    try:
        temp1 = float(operations.device_value('Temp1'))
        temp2 = float(operations.device_value('Temp2'))
    
        hum1 = float(operations.device_value('Hum1'))
        hum2 = float(operations.device_value('Hum2'))
    except:
        return

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

