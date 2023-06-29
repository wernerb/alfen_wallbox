import logging
from aiohttp import ClientSession

import requests
import time
import ssl
from enum import Enum
from datetime import timedelta
import datetime

from homeassistant.util import Throttle
from .const import DOMAIN, ALFEN_PRODUCT_MAP

HEADER_JSON = {"content-type": "alfen/json; charset=utf-8"}
POST_HEADER_JSON = {"content-type": "application/json"}

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)


class AlfenDevice:
    def __init__(self,
                 host: str,
                 name: str,
                 session: ClientSession,
                 username: str,
                 password: str) -> None:
        self.host = host
        self.name = name
        self._status = None
        self._session = session
        self.username = username
        self.info = None
        self.id = None
        if self.username is None:
            self.username = "admin"
        self.password = password
        self.properties = []
        # Default ciphers needed as of python 3.10
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.ssl = context

    async def init(self):
        await self.async_get_info()
        self.id = "alfen_{}".format(self.name)
        if self.name is None:
            self.name = f"{self.info.identity} ({self.host})"
        await self.async_update()

    @property
    def status(self):
        return self._status

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return {
            "identifiers": {(DOMAIN, self.name)},
            "manufacturer": "Alfen",
            "model": self.info.model,
            "name": self.name,
            "sw_version": self.info.firmware_version,
        }

    def _request(self, parameter_list):
        pass

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        await self._do_update()

    async def login(self):
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )

        _LOGGER.debug(f"Login response {response}")

    async def logout(self):
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        _LOGGER.debug(f"Logout response {response}")

    async def update_value(self, api_param, value):
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={api_param: {"id": api_param, "value": value}},
        )
        _LOGGER.info(f"Set {api_param} value {value} response {response}")

    async def _do_update(self):
        await self.login()

        properties = []
        for i in ["generic", "generic2", "meter1", "states", "temp"]:
            nextRequest = True
            offset = 0
            while (nextRequest):
                response = await self._session.request(
                    ssl=self.ssl,
                    method="GET",
                    headers=HEADER_JSON,
                    url=self.__get_url(
                        "prop?cat={}&offset={}".format(i, offset)
                    ),
                )
                _LOGGER.debug(f"Status Response {response}")

                response_json = await response.json(content_type=None)
                if response_json is not None:
                    properties += response_json["properties"]
                nextRequest = response_json["total"] > (
                    offset + len(response_json["properties"]))
                offset += len(response_json["properties"])

        await self.logout()

        self.properties = properties

    async def async_get_info(self):
        response = await self._session.request(
            ssl=self.ssl, method="GET", url=self.__get_url("info")
        )
        _LOGGER.debug(f"Response {response}")

        if response.status != 200:
            _LOGGER.debug("Info API not available, use generic info")

            generic_info = {
                "Identity": self.host,
                "FWVersion": "?",
                "Model": "Generic Alfen Wallbox",
                "ObjectId": "?",
                "Type": "?",
            }
            self.info = AlfenDeviceInfo(generic_info)
        else:
            response_json = await response.json(content_type=None)
            _LOGGER.debug(response_json)

            self.info = AlfenDeviceInfo(response_json)

    async def reboot_wallbox(self):
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("cmd"),
            json={"command": "reboot"},
        )
        _LOGGER.debug(f"Reboot response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )

    async def set_current_limit(self, limit):
        _LOGGER.debug(f"Set current limit {limit}A")
        if limit > 32 | limit < 1:
            return self.async_abort(reason="invalid_current_limit")

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"2129_0": {"id": "2129_0", "value": limit}},
        )
        _LOGGER.debug(f"Set current limit response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    async def set_rfid_auth_mode(self, enabled):
        _LOGGER.debug(f"Set RFID Auth Mode {enabled}")

        value = 0
        if enabled:
            value = 2

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"2126_0": {"id": "2126_0", "value": value}},
        )
        _LOGGER.debug(f"Set RFID Auth Mode {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    async def set_current_phase(self, phase):
        _LOGGER.debug(f"Set current phase {phase}")
        if phase != "L1" and phase != "L2" and phase != "L3":
            return self.async_abort(
                reason="invalid phase mapping allowed value: L1, L2, L3"
            )
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"2069_0": {"id": "2069_0", "value": phase}},
        )
        _LOGGER.debug(f"Set current phase response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    async def set_phase_switching(self, enabled):
        _LOGGER.debug(f"Set Phase Switching {enabled}")

        value = 0
        if enabled:
            value = 1

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"2185_0": {"id": "2185_0", "value": value}},
        )
        _LOGGER.debug(f"Set Phase Switching {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    async def set_green_share(self, value):
        _LOGGER.debug(f"Set green share value {value}%")
        if value < 0 | value > 100:
            return self.async_abort(reason="invalid_value")

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"3280_2": {"id": "3280_2", "value": value}},
        )
        _LOGGER.debug(f"Set green share value response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    async def set_comfort_power(self, value):
        _LOGGER.debug(f"Set Comfort Level {value}W")
        if value < 1400 | value > 5000:
            return self.async_abort(reason="invalid_value")

        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("login"),
            json={"username": self.username, "password": self.password},
        )
        response = await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=POST_HEADER_JSON,
            url=self.__get_url("prop"),
            json={"3280_3": {"id": "3280_3", "value": value}},
        )
        _LOGGER.debug(f"Set green share value response {response}")
        await self._session.request(
            ssl=self.ssl,
            method="POST",
            headers=HEADER_JSON,
            url=self.__get_url("logout"),
        )
        await self._do_update()

    def __get_url(self, action):
        return "https://{}/api/{}".format(self.host, action)


#     def auth_mode_as_str(self, code):
#         switcher = {0: "Plug and Charge", 2: "RFID"}
#         return switcher.get(code, "Unknown")

# #    def solar_charging_mode(self, code):
# #        switcher = {0: "Disable", 1: "Comfort", 2: "Green"}
# #        return switcher.get(code, "Unknown")


class AlfenDeviceInfo:
    def __init__(self, response) -> None:
        self.identity = response["Identity"]
        self.firmware_version = response["FWVersion"]
        self.model_id = response["Model"]

        if ALFEN_PRODUCT_MAP[self.model_id] is None:
            self.model = self.model_id
        else:
            self.model = f"{ALFEN_PRODUCT_MAP[self.model_id]} ({self.model_id})"

        self.object_id = response["ObjectId"]
        self.type = response["Type"]
