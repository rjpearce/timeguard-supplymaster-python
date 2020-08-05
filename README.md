# timeguard-supplymaster-python

This Python module will provides an open-source implementation of the client API used by the Timeguard's Supplymaster application. This is typically used to control [Timeguard's FSTWIFI Wi-Fi Controlled Fused Spur](https://www.timeguard.com/products/time/immersion-and-general-purpose-timeswitches/wi-fi-controlled-fused-spur)

This implementation is based on my [investigation of the API](https://github.com/rjpearce/timeguard-supplymaster)

It is currently in the early stages of development, contributions are always welcome but it will be a fast moving target

## Legal Disclaimer

This software is un-official and is not endorsed or associated with Timeguard Limited in any way shape or form.

This information used has been gathered legally using the Supplymaster Android application and [Charles Proxy](https://www.charlesproxy.com).

This software is being developed to aid my own personal efforts to automate scheduling of my FSTWIFI device for [Octopus Agile](https://octopus.energy/agile/)

The software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. in no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the softwares or the use or mis-used or other dealings in the software.

## Setup

1. Clone the repo

  ```bash
  git clone git@github.com:rjpearce/timeguard-supplymaster-python.git timeguard
  ```

1. Create ~/.timeguard.yaml

  ```bash
  ---
  username: tg-username
  password: tg-password
  use_cache: False
  ...
  ```
## Usage

List all devices, programs and time slots.

```python
tg = TimeGuard()
tg.refresh_devices()
for device in tg.devices:
  print(device.name, device.id)
  for program in device.programs:
    print(program.id, program.name)
    print(program.time_slots)
```

For more examples see the examples folder.

## Contribute

Please do feel free to fork this module it enhance it for the benefit of everyone