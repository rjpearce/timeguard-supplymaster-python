""" Example showing how to update the current mode of the first Timeguard device """
from timeguard_supplymaster import Client, Mode

client = Client()
device = client.refresh_devices()[0]
print(device.set_mode(Mode.ON))
print(device.set_mode(Mode.OFF))
