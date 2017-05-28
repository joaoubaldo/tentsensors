from datetime import datetime

from tentsensord import common


def child_name_by_id(id_):
    """ get device name by id """
    for k, v in common.config['child_map'].items():
        if v == int(id_):
            return k
    return None


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")
