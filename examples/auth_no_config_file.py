"""
    An alternative to using the .yaml file for configuration
    to override the config-file by passing "use_config_file=False"
    and specifying your api username and password

    GitHub: joemadd3n
    Contact: joe@madden.cloud
"""

from timeguard_supplymaster import Client

client = Client(
    use_config_file=False,
    api_username='your_api_username',
    api_password='your_api_password'
)

client.refresh_devices()
