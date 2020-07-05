""" Timeguard """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
from pathlib import Path

class Device:
  name = ''
  id = ''
  attributes = {}
  timeguard = None

  def __init__(self, timeguard, attributes):
    self.timeguard = timeguard
    self.attributes = attributes
    self.name = attributes['name']
    self.id = attributes['device_id']
    self.refresh_device_info()

  def refresh_device_info(self):
    self.timeguard.api_request('GET',f'wifi_boxes/data/user_id/{self.timeguard.user_id}/wifi_box_id/{self.id}/token/{self.timeguard.token}')

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

  def __init__(self, config_path=f'{str(Path.home())}/.timeguard.yaml', cache_folder=f'{os.getcwd()}/cache'):
    self.config = self.read_config(config_path)
    self.validate_config()
    self.cache_folder = cache_folder
    self.base_url = 'https://www.cloudwarm.net/TimeGuard/api/Android/v_1'

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
    cache_file = f'{uri.replace("/","_")}.json'
    if self.config['use_cache']:
      with open(f'{self.cache_folder}/{cache_file}') as data_file:    
        return json.load(data_file)
    headers = {'User-Agent': 'okhttp/3.3.1'}
    timeout = (self.connect_timeout, self.read_timeout)
    if type == 'PUT':
      response = requests.put(f'{self.base_url}/{uri}', headers=headers, data=data, timeout=timeout)
    elif type == 'GET':
      response = requests.get(f'{self.base_url}/{uri}', headers=headers, timeout=timeout)
    if response.status_code == 200:
      response_json = response.json()
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

def main(): 
  tg = TimeGuard()
  pprint(tg.refresh_devices())

if __name__ == "__main__":
  main()
