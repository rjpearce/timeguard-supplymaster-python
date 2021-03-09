""" Implementation of a Timeguard Device """
from .program import Program
from .mode import Mode

class Device:
    """ Timeguard device """
    # pylint: disable=too-many-instance-attributes
    name = ''
    id = ''
    attributes = {}
    timeguard = None
    programs = []
    holiday = False
    holiday_start = ''
    holiday_end = ''
    boost_start_time = '0'
    boost_hour = '0'
    advance = '0'
    mode = None

    def __init__(self, timeguard, attributes):
        # pylint: disable=too-many-instance-attributes
        self.attributes = attributes
        self.name = attributes['name']
        # pylint: disable=invalid-name
        self.id = attributes['device_id']
        self.online = bool(int(attributes['online']))
        self.timeguard = timeguard
        self.refresh_device_info()

    def refresh_device_info(self):
        """ Update the local device info with the Timeguard API """
        device_json = self.timeguard.api_request('GET',
            f'wifi_boxes/data/user_id/{self.timeguard.user_id}'
            f'/wifi_box_id/{self.id}'
            f'/token/{self.timeguard.token}'
        )
        message = device_json['message']
        program_list_json = self.timeguard.api_request('GET',
            f'wifi_boxes/program_list'
            f'/user_id/{self.timeguard.user_id}'
            f'/wifi_box_id/{self.id}'
            f'/token/{self.timeguard.token}'
        )
        for program in program_list_json['message']['namelist']:
            program_json = self.timeguard.api_request('GET',
                f'wifi_boxes/program'
                f'/user_id/{self.timeguard.user_id}'
                f'/wifi_box_id/{self.id}'
                f'/index/{program["id"]}'
                f'/token/{self.timeguard.token}'
            )
            self.programs.append(
                Program(
                    program['id'],
                    program['name'],
                    program_json['message']['program'],
                    self
                )
            )
        self.holiday       = bool(int(message['holiday']['enable']))
        self.holiday_start = message['holiday']['start']
        self.holiday_end   = message['holiday']['end']
        self.advance       = bool(int(message['advance']))
        self.mode          = Mode(int(message['work_mode']))

    def set_mode(self, mode):
        """ Change the current mode for the device """
        data = {
            "work_mode": mode.value,
            "token": self.timeguard.token,
            "user_id": self.timeguard.user_id,
            "wifi_box_id": self.id,
        }
        self.mode = mode
        return self.timeguard.api_request("PUT", 'wifi_boxes/work_mode', data)

    def __repr__(self):
        return f'{self.name}'
