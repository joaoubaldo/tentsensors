import json

import cherrypy

from tentsensord import common
from tentsensord import operations
from tentsensord.cli import json_serial
from tentsensord.utils import child_name_by_id


@cherrypy.popargs('device_name')
class DeviceWebService(object):
    exposed = True

    def GET(self, device_name=None):
        cherrypy.response.headers['Content-Type'] = u"application/json"

        if not device_name or device_name not in common.current_state:
            return json.dumps(common.current_state,
                default=json_serial).encode('utf8')

        return json.dumps(common.current_state[device_name],
            default=json_serial).encode('utf8')

    def POST(self, device_name=None):
        cherrypy.response.status = "501 Not Implemented"
        return

    def PUT(self, device_name=None, value=None):
        if not device_name or device_name not in common.current_state:
            cherrypy.response.status = "404 Device not found"
            return

        if value not in ('0', '1'):
            cherrypy.response.status = "200 Bad request"
            return

        if value == '1':
            operations.turn_on(device_name)
        else:
            operations.turn_off(device_name)

        cherrypy.response.headers['Content-Type'] = u"application/json"

        response = {
            'device': common.current_state[device_name],
            'success': True
        }

        return json.dumps(response, default=json_serial).encode('utf8')

    def DELETE(self, device_name=None):
        cherrypy.response.status = "501 Not Implemented"
        return


@cherrypy.popargs('action')
class ControlWebService(object):
    exposed = True
    valid_actions = ['disable_control', 'enable_control']

    def GET(self, action=None):
        response = {'available_actions': ControlWebService.valid_actions}
        return json.dumps(response, default=json_serial).encode('utf8')

    def POST(self, action=None):
        if not action or action not in ControlWebService.valid_actions:
            cherrypy.response.status = "200 Bad request"

        if action == 'disable_control':
            common.logic_enabled = False
            print("auto control disabled")
        elif action == 'enable_control':
            common.logic_enabled = True
            print("auto control enabled")

        cherrypy.response.headers['Content-Type'] = u"application/json"
        response = {
            'action': action,
            'success': True
        }

        return json.dumps(response, default=json_serial).encode('utf8')
