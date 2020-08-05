
import sys
sys.path.append("..")
from timeguard import TimeGuard

tg = TimeGuard()
tg.refresh_devices()
for device in tg.devices:
  print(device.name, device.id)
  for program in device.programs:
    everyday = { 'Mon': True, 'Tue': True, 'Wed': True, 'Thu': True, 'Fri': True, 'Sat': True, 'Sun': True}
    if program.id == '0':
      program.time_slots[0].set_time(everyday, '02:30', '03:00')
      program.time_slots[1].set_time(everyday, '03:00', '04:00')
      program.time_slots[2].set_time(everyday, '13:30', '14:00')
      program.time_slots[3].set_time(everyday, '14:30', '15:00')
      program.time_slots[4].reset()
      program.save()
    else:
      program.name = f'Program {program.id}'
      program.time_slots[0].reset()
    print(program.id, program.name)
    print(program.time_slots)
