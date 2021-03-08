# GitHub: joemadd3n
# Contact: joe@madden.cloud
# Date: 08/03/2021


from timeguard_supplymaster import Client

# An alternative to using the .yaml file for configuation is to over-ride the config-file by passing "use_config_file=False" and 
# specifying your api username and password
client = Client(use_config_file=False, api_username='your_api_username', api_password='your_api_password')

client.refresh_devices()

