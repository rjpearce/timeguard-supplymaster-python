""" Timeguard """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
from pathlib import Path

""" A single time entry when the device should be on or off """
class TimeSlot:
  attributes = {}
  DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  def __init__(self, attributes):
    self.attributes = attributes

  def translate_days_value(self, days):
    translated_days = []
    for dow in days:
      translated_days.append(self.DAYS[int(dow)])
    if (len(translated_days) == 0):
      return 'None'
    return ','.join(translated_days)

  def set_time(self, days, start_time, end_time, start_enabled=True, end_enabled = True):
    for day in days:
      if day in self.DAYS:
        self.attributes['map'][str(int(self.DAYS.index(day)))] = str(int(days[day]))
        self.attributes['end']['enable'] = str(int(end_enabled))
        self.attributes['end']['time'] = end_time
        self.attributes['start']['enable'] = str(int(start_enabled))
        self.attributes['start']['time'] = start_time
      else:
        print(f'Unknown day {day}')

  def reset(self):
    for day in self.DAYS:
      self.attributes['map'][str(self.DAYS.index(day))] = '0'
      self.attributes['end']['enable'] = '0'
      self.attributes['end']['time'] = '00:00'
      self.attributes['start']['enable'] = '0'
      self.attributes['start']['time'] = '00:00'

  def to_json(self):
    return {
      "start": self.attributes['start'],
      "end": self.attributes['end'],
      "map": self.attributes['map']
    }

  def __repr__(self):
    days = self.translate_days_value(self.attributes['map'])
    start_time = self.attributes['start']['time']
    start_enabled = bool(int(self.attributes['start']['enable']))
    end_time = self.attributes['end']['time']
    end_enabled = bool(int(self.attributes['end']['enable']))
    return "\n%s(%s) to %s(%s) on %s" % (start_time, start_enabled, end_time, end_enabled, days)

class Program:
  id = ''
  name = ''
  time_slots = []
  device = None

  def __init__(self, id, name, attributes, device):
    self.id = id
    self.name = name
    self.device = device
    self.time_slots = []
    for time_slot in attributes:
      self.time_slots.append(TimeSlot(time_slot))

  def save(self):
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
    response_json = self.device.timeguard.api_request('PUT','wifi_boxes/program', data)
  
  def reset_all_time_slots(self):
    for time_slot in self.time_slots:
      time_slot.reset()

  def __repr__(self):
    return "Program %s (%s):\n  %s" % (self.id, self.name, self.time_slots)

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

class TimeGuard:
  """ Implements the TimeGuard API """
  config = {}
  devices = []
  connect_timeout = 10
  read_timeout = 30
  cache_folder = ''
  base_url = ''
  token = ''
  user_id = ''
  HEADERS = {'User-Agent': 'okhttp/3.3.1'}
  BASE_URL = 'https://www.cloudwarm.net/TimeGuard/api/Android/v_1'
  EVERYDAY = { 'Mon': True, 'Tue': True, 'Wed': True, 'Thu': True, 'Fri': True, 'Sat': True, 'Sun': True}

  def __init__(self, config_path=f'{str(Path.home())}/.timeguard.yaml', cache_folder=f'{os.getcwd()}/cache'):
    self.config = self.read_config(config_path)
    self.validate_config()
    self.cache_folder = cache_folder
    os.makedirs(cache_folder, exist_ok=True)

  def read_config(self, config_path):
    """ Read the configuration file """
    with open(config_path, 'r') as config_file:
      return yaml.safe_load(config_file.read())

  def validate_config(self):
    """ Validate the config """
    if 'username' not in self.config:
      raise Exception('username missing from config')
    if 'password' not in self.config:
      raise Exception('password missing from config')
    if 'use_cache' not in self.config:
      self.config['use_cache'] = False

  def api_request(self, type, uri, data=None):
    response = None
    cache_file = f'{uri.replace(self.token,"").replace("/","_")}.json'
    if self.config['use_cache']:
      with open(f'{self.cache_folder}/{cache_file}') as data_file:    
        return json.load(data_file)
    timeout = (self.connect_timeout, self.read_timeout)
    if type == 'PUT':
      print('PUT', f'{self.BASE_URL}/{uri}', data, self.HEADERS, timeout)
      response = requests.put(f'{self.BASE_URL}/{uri}', data=data, headers=self.HEADERS, timeout=timeout)
    elif type == 'GET':
      print('GET', f'{self.BASE_URL}/{uri}', self.HEADERS, timeout)
      response = requests.get(f'{self.BASE_URL}/{uri}', headers=self.HEADERS, timeout=timeout)
    if response.status_code == 200:
      print(response.status_code)
      response_json = response.json()
      pprint(response_json)
      status_file = open(f'{self.cache_folder}/{cache_file}', 'w')
      status_file.write(json.dumps(response_json))
      status_file.close()
      return response_json
    else:
      raise Exception(f'Login request failed: {response.status_code}')

  def refresh_devices(self):
    data = f'username={self.config["username"]}&password={self.config["password"]}'
    response_json = self.api_request('PUT', 'users/login', data)
    self.token = response_json['message']['user']['token']
    self.user_id = response_json['message']['user']['id']
    for device in response_json['message']['wifi_box']:
      self.devices.append(Device(self, device))
    return self.devices
