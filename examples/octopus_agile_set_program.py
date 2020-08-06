
from timeguard_supplymaster import Client
from OctopusAgile import Agile
from pprint import pprint
from datetime import date, datetime, timedelta
from collections import OrderedDict

EAST_ENGLAND='A'

agile = Agile(EAST_ENGLAND)
rates = agile.get_rates(f'{date.today()}T00:00:00Z',  f'{date.today()}T23:59:50Z')

requirements = [
  {
    "slots": 1, 
    "time_from": f'{date.today()}T00:00:00Z',
    "time_to": f'{date.today()}T08:00:00Z'
  },
  {
    "slots": 1, 
    "time_from": f'{date.today()}T12:00:00Z',
    "time_to": f'{date.today()}T16:00:00Z'
  }
]
total_slots = 3
# Provide 3 time slots that fulfil my minimum requirements 
time_slots = agile.get_min_times(total_slots, rates['date_rates'], requirements)


client = Client()
client.refresh_devices()
for device in client.devices:
  for program in device.programs:
    program.reset_all_time_slots()
    if program.id == '0':
      for slot in range(total_slots):
        #list(time_slots.keys())[slot]
        start = datetime.strptime(list(time_slots.keys())[slot], "%Y-%m-%dT%H:%M:%SZ")
        end = start + timedelta(minutes=30)
        print(slot, str(start.time()), str(end.time()))
        program.time_slots[slot].set_time(client.EVERYDAY, str(start.time()), str(end.time()))
      program.save()

pprint(time_slots)