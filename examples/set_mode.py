from timeguard_supplymaster import Client
from timeguard_supplymaster import Mode

client = Client()
device = client.refresh_devices()[0]
print(device.set_mode(Mode.ON))
