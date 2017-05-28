import unittest

config_content = """
{
    "device": "/dev/ttyUSB0",
    "logic_script": "/invalid/logic.py",
    "baud_rate": 115200,
    "loop_sleep": 5,
    "child_map": {
        "Hum1": 10,
        "Hum2": 11,
        "Temp1": 12,
        "Temp2": 13,
        "Resistor": 14,
        "Fan": 15,
        "Extractor": 16,
        "LED": 17,
        "HPS": 18,
        "Humidifier": 19
    },
    "vars": {
        "day_start": 16,
        "day_end": 6,
        "target_night_temp": 20,
        "target_day_temp": 25
    }
}
"""

def mock_gw():
    from tentsensord import common
    from tentsensord.cli import update_child_state

    class MockedGw:
        def set_child_value(self, sensor_id, child_id, value_type, value,
                            **kwargs):
            update_child_state(child_id, value)

        def stop(self):
            pass
    common.gw_thread = MockedGw()


class MissingLogicFileTestCase(unittest.TestCase):
    def setUp(self):
        mock_gw()

    def test(self):
        from tentsensord.cli import load_logic_module
        from tentsensord.common import load_config
        import json

        load_config(json.loads(config_content))
        self.assertRaises(FileNotFoundError, load_logic_module)

class MissingConfigFileTestCase(unittest.TestCase):
    def setUp(self):
        mock_gw()

    def test(self):
        from tentsensord.cli import load_logic_module
        from tentsensord.common import load_config
        from tentsensord import common

        common.config_file = 'invalid_file'
        self.assertRaises(FileNotFoundError, load_config)

class ChildStateUpdateTestCase(unittest.TestCase):
    def setUp(self):
        mock_gw()

    def test(self):
        from tentsensord.cli import update_child_state
        from tentsensord.common import load_config
        from tentsensord import common
        import json

        load_config(json.loads(config_content))
        update_child_state(common.config['child_map']["Hum1"], 1)
        self.assertEqual(len(common.current_state), 1)
        self.assertTrue("Hum1" in common.current_state)
        self.assertEqual(common.current_state["Hum1"]["value"], '1')

class GetChildByIdTestCase(unittest.TestCase):
    def setUp(self):
        mock_gw()

    def test_get_child_name_by_id(self):
        from tentsensord.common import load_config
        from tentsensord.cli import child_name_by_id
        from tentsensord import common
        import json

        load_config(json.loads(config_content))
        self.assertEqual(
            child_name_by_id(common.config['child_map']["Hum1"]),
            "Hum1")

class DeviceToggleTestCase(unittest.TestCase):
    def setUp(self):
        mock_gw()

    def test_device_toggle(self):
        from tentsensord.common import load_config
        from tentsensord.cli import child_name_by_id
        from tentsensord import common
        from tentsensord import operations
        import json

        load_config(json.loads(config_content))

        self.assertIsNone(operations.device_value("Extractor"))
        operations.turn_on("Extractor")
        self.assertEqual(operations.device_value("Extractor"), '1')
        operations.turn_off("Extractor")
        self.assertEqual(operations.device_value("Extractor"), '0')
        operations.toggle("Extractor")
        self.assertEqual(operations.device_value("Extractor"), '1')
