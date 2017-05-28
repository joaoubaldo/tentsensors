from datetime import datetime
from datetime import timedelta

from tentsensord import operations
from tentsensord import common

def is_day(now=None):
    if not now:
        now = datetime.now()

    print(common.config)
    start = common.config['vars']['day_start']
    end = common.config['vars']['day_end']

    if start > end:
        return now >= now.replace(hour=start) or now < now.replace(hour=end)
    else:
        return now >= now.replace(hour=start) and now < now.replace(hour=end)


def day_logic():
    now = datetime.now()
    if not operations.last_update('Extractor') or \
    (now - operations.last_update('Extractor')) >= timedelta(minutes=30):
        operations.toggle('Extractor')

    if not operations.last_update('Fan') or \
    (now - operations.last_update('Fan')) >= timedelta(minutes=15):
        operations.toggle('Fan')


def night_logic():
    now = datetime.now()
    if not operations.last_update('Extractor') or \
    (now - operations.last_update('Extractor')) >= timedelta(minutes=30):
        operations.toggle('Extractor')

    if not operations.last_update('Fan') or \
    (now - operations.last_update('Fan')) >= timedelta(minutes=15):
        operations.toggle('Fan')


def run():
    if is_day():
        day_logic()
    else:
        night_logic()
