
from .program import Program

class Device:
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

  def __init__(self, timeguard, attributes):
    self.attributes = attributes
    self.name = attributes['name']
    self.id = attributes['device_id']
    self.online = bool(int(attributes['online']))
    self.timeguard = timeguard
    self.refresh_device_info()

  def refresh_device_info(self):
    device_json = self.timeguard.api_request('GET',f'wifi_boxes/data/user_id/{self.timeguard.user_id}/wifi_box_id/{self.id}/token/{self.timeguard.token}')
    message = device_json['message']
    program_list_json = self.timeguard.api_request('GET',f'wifi_boxes/program_list/user_id/{self.timeguard.user_id}/wifi_box_id/{self.id}/token/{self.timeguard.token}')
    for program in program_list_json['message']['namelist']:
      program_json = self.timeguard.api_request('GET',f'wifi_boxes/program/user_id/{self.timeguard.user_id}/wifi_box_id/{self.id}/index/{program["id"]}/token/{self.timeguard.token}')
      self.programs.append(Program(program['id'], program['name'], program_json['message']['program'], self))
    self.holiday = bool(int(message['holiday']['enable']))
    self.holiday_start  = message['holiday']['start']
    self.holiday_end  = message['holiday']['end']
    self.advance = bool(int(message['advance']))

  def __repr__(self):
    return f'{self.name}'