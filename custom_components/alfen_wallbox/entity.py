import logging

import ssl
from config.custom_components.alfen_wallbox.alfen import HEADER_JSON, POST_HEADER_JSON, AlfenDevice, AlfenStatus
from homeassistant.core import DOMAIN
from homeassistant.helpers.entity import DeviceInfo, Entity

_LOGGER = logging.getLogger(__name__)


class AlfenEntity(Entity):

    def __init__(self, device: AlfenDevice) -> None:
        self._host = device.host
        self._attr_name = device.name
        self._status = device.status
        self._session = device._session
        self._username = device.username
        if self._username is None:
            self._username = "admin"
        self._password = device.password
        # Default ciphers needed as of python 3.10
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.ssl = context
        self.device = device

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device.id)},
            manufacturer="Alfen",
            model=self.device.info.model,
            name=self.name,
            sw_version=self.device.info.firmware_version,
        )

    async def async_added_to_hass(self) -> None:
        """Add listener for state changes."""
        await super().async_added_to_hass()

    async def _on_update(self) -> None:
        await self.login()

        # max 32 ids each time
        response = await self._session.request(
            ssl=self.ssl,
            method="GET",
            headers=HEADER_JSON,
            url=self.__get_url(
                "prop?ids=2060_0,2056_0,2221_3,2221_4,2221_5,2221_A,2221_B,2221_C,2221_16,2201_0,2501_2,2221_22,2129_0,2126_0,2068_0,2069_0,2062_0,2064_0,212B_0,212D_0,2185_0,2053_0,2067_0,212F_1,212F_2,212F_3,2100_0,2101_0,2102_0,2104_0,2105_0"
            ),
        )
        _LOGGER.debug(f"Status Response {response}")

        response_json = await response.json(content_type=None)
        _LOGGER.debug(response_json)

        response2 = await self._session.request(
            ssl=self.ssl,
            method="GET",
            headers=HEADER_JSON,
            url=self.__get_url(
                "prop?ids=2057_0,2112_0,2071_1,2071_2,2072_1,2073_1,2074_1,2075_1,2076_0,2078_1,2078_2,2079_1,207A_1,207B_1,207C_1,207D_1,207E_1,207F_1,2080_1,2081_0,2082_0,2110_0,3280_1,3280_2,3280_3,3280_4"
            ),
        )
        _LOGGER.debug(f"Status Response {response2}")

        response_json2 = await response2.json(content_type=None)
        _LOGGER.debug(response_json2)

        await self.logout()

        response_json_combined = response_json
        if response_json2 is not None:
            response_json_combined["properties"] = (
                response_json["properties"] + response_json2["properties"]
            )
            response_json_combined["total"] = (
                response_json["total"] + response_json2["total"]
            )

        _LOGGER.debug(response_json_combined)

        self._status = AlfenStatus(response_json_combined, self._status)
        self.async_write_ha_state()

    def __get_url(self, action):
        return "https://{}/api/{}".format(self._host, action)

    async def login(self):
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self._username, "password": self._password},
        )

    async def logout(self):
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )

    async def update_state(self, api_param, value):
        """Get the state of the entity."""

        await self.login()

        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={api_param: {"id": api_param, "value": value}},
        )
        _LOGGER.info(f"Set {api_param} value {value} response {response}")

        await self.logout()
