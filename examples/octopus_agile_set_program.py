
import timeguard_supplymaster
import OctopusAgile
from pprint import pprint
from pytz import utc, timezone
from datetime import date, datetime, timedelta
from collections import OrderedDict

# DNO Operators - https://en.wikipedia.org/wiki/Distribution_network_operator
EAST_ENGLAND='A'
EAST_MIDLANDS='B'
LONDON='C'
NORTH_WALES_MERSEYSIDE_AND_CHESHIRE='D'
WEST_MIDLANDS='E'
NORTH_EAST_ENGLAND='F'
NORTH_WEST_ENGLAND='G'
NORTH_SCOTLAND='P'
SOUTH_SCOTLAND='N'
SOUTH_EAST='J'
SOUTHERN='H'
SOUTH_WALES='K'
SOUTH_WEST='L'
YORKSHIRE='M'

# Local Timezone
LDN=timezone('Europe/London')

# The day you want to schedule
DAY = date.today() + timedelta(days=1)

# Total number of slots that you want
TOTAL_SLOTS = 3

# Requirements around the slots in local time
requirements = [
   {
     "slots": 1, 
     "time_from": f'{DAY}T00:00:00Z',
     "time_to": f'{DAY}T09:00:00Z'
   },
   {
     "slots": 1, 
     "time_from": f'{DAY}T12:00:00Z',
     "time_to": f'{DAY}T16:00:00Z'
   }
]

# Try to get these into the upstream Agile repo
def localise_raw_rates(rates, tz):
  localised_rates = []
  for rate in rates: 
    valid_from = datetime.strptime(rate['valid_from'], "%Y-%m-%dT%H:%M:%SZ")
    valid_to = datetime.strptime(rate['valid_to'], "%Y-%m-%dT%H:%M:%SZ")
    rate['valid_from'] = tz.localize(valid_from).strftime("%Y-%m-%dT%H:%M:%SZ")
    rate['valid_to'] = tz.localize(valid_to).strftime("%Y-%m-%dT%H:%M:%SZ")
    localised_rates.append(rate)
  return localised_rates

def localise_datetime(timestamp, tzone):
  utc_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
  offset = tzone.localize(utc_timestamp).dst()
  localised_timestamp = tzone.localize(utc_timestamp) + offset
  return localised_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

def unlocalise_datetime(timestamp, tzone):
  localised_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
  offset = tzone.localize(localised_timestamp).dst()
  utc_timestamp = tzone.localize(localised_timestamp) - offset
  return utc_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

def localise_rates(rates, tzone):
  localised_rates = OrderedDict()
  for timestamp, price in rates.items():
    localised_rates[localise_datetime(timestamp, tzone)]=price
  return localised_rates

# Convert requirements from human friendly local time into UTC
for requirement in requirements:
  requirement['time_from'] = unlocalise_datetime(requirement['time_from'], LDN)
  requirement['time_to'] = unlocalise_datetime(requirement['time_to'], LDN)

# Obtain the rates from Octopus
agile = OctopusAgile.Agile(EAST_ENGLAND)
rates = agile.get_rates(f'{DAY}T00:00:00Z',  f'{DAY}T23:59:50Z')['date_rates']

# Workout the cheapest slots meeting our requirements
time_slots = agile.get_min_times(TOTAL_SLOTS, rates, requirements)
localised_time_slots = localise_rates(time_slots, LDN)

# Connect to the timeguard API
timeguard = timeguard_supplymaster.Client()
timeguard.refresh_devices()
for device in timeguard.devices:
  for program in device.programs:
    program.reset_all_time_slots()
    if program.id == '0':
      # Set the program time slots to the cheapest time slots
      for slot in range(TOTAL_SLOTS):
        start = datetime.strptime(list(localised_time_slots.keys())[slot], "%Y-%m-%dT%H:%M:%SZ")
        end = start + timedelta(minutes=30)
        print(slot, str(start.time()), str(end.time()))
        schedule = timeguard.NEVER
        schedule[DAY.strftime("%a")] = True
        program.time_slots[slot].set_time(schedule, str(start.time()), str(end.time()))
      program.save()

pprint(localised_time_slots)