""" Implementation of a Timeguard Program """
from pprint import pprint
import json
from .timeslot import TimeSlot

class Program:
    """ Implements the TimeGuard API Program """
    id = ''
    name = ''
    time_slots = []
    device = None
    # pylint: disable=invalid-name
    def __init__(self, program_id, name, attributes, device):
        self.id = program_id
        self.name = name
        self.device = device
        self.time_slots = []
        for time_slot in attributes:
            self.time_slots.append(TimeSlot(time_slot))

    def save(self):
        """ Persist the current state with the Timeguard API """
        slots = []
        for time_slot in self.time_slots:
            slots.append(time_slot.to_json())
        data = {
            "program": json.dumps({
                "id": self.id,
                "name": self.name,
                "program": slots
            }),
            "token": self.device.timeguard.token,
            "user_id": self.device.timeguard.user_id,
            "wifi_box_id": self.device.id
        }
        pprint(data)
        response_json = self.device.timeguard.api_request(
            'PUT', 'wifi_boxes/program', data)
        pprint(response_json)

    def reset_all_time_slots(self):
        """ Reset all of the Timeslots to default """
        for time_slot in self.time_slots:
            time_slot.reset()

    def __repr__(self):
        return "Program %s (%s):\n  %s" % (self.id, self.name, self.time_slots)
