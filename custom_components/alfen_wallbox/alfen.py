import logging
from aiohttp import ClientSession

import ssl
from datetime import timedelta

from homeassistant.util import Throttle
from .const import CAT, CAT_GENERIC, CAT_GENERIC2, CAT_METER1, CAT_OCPP, CAT_STATES, CAT_TEMP, CMD, DOMAIN, ALFEN_PRODUCT_MAP, ID, METHOD_GET, METHOD_POST, OFFSET, INFO, LOGIN, LOGOUT, PARAM_COMMAND, PARAM_PASSWORD, PARAM_USERNAME, PROP, PROPERTIES, TOTAL, VALUE

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
            method=METHOD_POST,
            headers=HEADER_JSON,
            url=self.__get_url(LOGIN),
            json={PARAM_USERNAME: self.username,
                  PARAM_PASSWORD: self.password},
        )

        _LOGGER.debug(f"Login response {response}")
        return response.status == 200

    async def logout(self):
        response = await self._session.request(
            ssl=self.ssl,
            method=METHOD_POST,
            headers=HEADER_JSON,
            url=self.__get_url(LOGOUT),
        )
        _LOGGER.debug(f"Logout response {response}")
        return response.status == 200

    async def _update_value(self, api_param, value):
        response = await self._session.request(
            ssl=self.ssl,
            method=METHOD_POST,
            headers=POST_HEADER_JSON,
            url=self.__get_url(PROP),
            json={api_param: {ID: api_param, VALUE: value}},
        )
        _LOGGER.debug(f"Set {api_param} value {value} response {response}")
        return response.status == 200

    async def _get_value(self, api_param):
        response = await self._session.request(
            ssl=self.ssl,
            method=METHOD_GET,
            headers=HEADER_JSON,
            url=self.__get_url(
                "{}?{}={}".format(PROP, ID, api_param)
            ),
        )
        _LOGGER.debug(f"Status Response {response}")
        response_json = await response.json(content_type=None)
        if self.properties is None:
            self.properties = []
        for resp in response_json[PROPERTIES]:
            for prop in self.properties:
                if prop[ID] == resp[ID]:
                    prop[VALUE] = resp[VALUE]
                    break

    async def _do_update(self):
        await self.login()

        properties = []
        for cat in (CAT_GENERIC, CAT_GENERIC2, CAT_METER1, CAT_STATES, CAT_TEMP, CAT_OCPP):
            nextRequest = True
            offset = 0
            while (nextRequest):
                response = await self._session.request(
                    ssl=self.ssl,
                    method=METHOD_GET,
                    headers=HEADER_JSON,
                    url=self.__get_url("{}?{}={}&{}={}".format(
                        PROP, CAT, cat, OFFSET, offset)),
                )
                _LOGGER.debug(f"Status Response {response}")

                response_json = await response.json(content_type=None)
                if response_json is not None:
                    properties += response_json[PROPERTIES]
                nextRequest = response_json[TOTAL] > (
                    offset + len(response_json[PROPERTIES]))
                offset += len(response_json[PROPERTIES])

        await self.logout()

        self.properties = properties

    async def async_get_info(self):
        response = await self._session.request(
            ssl=self.ssl, method=METHOD_GET, url=self.__get_url(INFO)
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
        await self.login()

        response = await self._session.request(
            ssl=self.ssl,
            method=METHOD_POST,
            headers=POST_HEADER_JSON,
            url=self.__get_url(CMD),
            json={PARAM_COMMAND: "reboot"},
        )
        _LOGGER.debug(f"Reboot response {response}")
        await self.logout()

    async def set_value(self, api_param, value):

        logged_in = await self.login()
        # if not logged in, we can't set the value, show error
        if not logged_in:
            return self.async_abort(reason="Unable to authenticate to wallbox")

        success = await self._update_value(api_param, value)
        await self.logout()
        if success:
            # we expect that the value is updated so we are just update the value in the properties
            for prop in self.properties:
                if prop[ID] == api_param:
                    _LOGGER.debug(f"Set {api_param} value {value}")
                    prop[VALUE] = value
                    break

    async def get_value(self, api_param):
        await self.login()
        await self._get_value(api_param)
        await self.logout()

    async def set_current_limit(self, limit):
        _LOGGER.debug(f"Set current limit {limit}A")
        if limit > 32 | limit < 1:
            return self.async_abort(reason="invalid_current_limit")
        self.set_value("2129_0", limit)

    async def set_rfid_auth_mode(self, enabled):
        _LOGGER.debug(f"Set RFID Auth Mode {enabled}")

        value = 0
        if enabled:
            value = 2

        self.set_value("2126_0", value)

    async def set_current_phase(self, phase):
        _LOGGER.debug(f"Set current phase {phase}")
        if phase not in ('L1', 'L2', 'L3'):
            return self.async_abort(
                reason="invalid phase mapping allowed value: L1, L2, L3"
            )
        self.set_value("2069_0", phase)

    async def set_phase_switching(self, enabled):
        _LOGGER.debug(f"Set Phase Switching {enabled}")

        value = 0
        if enabled:
            value = 1

        self.set_value("2185_0", value)

    async def set_green_share(self, value):
        _LOGGER.debug(f"Set green share value {value}%")
        if value < 0 | value > 100:
            return self.async_abort(reason="invalid_value")
        self.set_value("3280_2", value)

    async def set_comfort_power(self, value):
        _LOGGER.debug(f"Set Comfort Level {value}W")
        if value < 1400 | value > 5000:
            return self.async_abort(reason="invalid_value")
        self.set_value("3280_3", value)

    def __get_url(self, action):
        return "https://{}/api/{}".format(self.host, action)


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
