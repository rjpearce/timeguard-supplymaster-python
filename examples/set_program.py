
import sys
sys.path.append("..")
from timeguard import TimeGuard

tg = TimeGuard()
tg.refresh_devices()
for device in tg.devices:
  print(device.name, device.id)
  for program in device.programs:
    program.reset_all_time_slots()
    if program.id == '0':
      program.time_slots[0].set_time(tg.EVERYDAY, '02:30', '03:00')
      program.time_slots[1].set_time(tg.EVERYDAY, '03:00', '04:00')
      program.time_slots[2].set_time(tg.EVERYDAY, '13:30', '14:00')
      program.time_slots[3].set_time(tg.EVERYDAY, '14:30', '15:00')
      program.save()
    print(program.id, program.name)
    print(program.time_slots)
