import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
from pathlib import Path
from .device import Device

class Client:
  """ Implements the TimeGuard Client """
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
