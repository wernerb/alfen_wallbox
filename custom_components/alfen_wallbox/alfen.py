import logging

import requests
import time
from enum import Enum
from datetime import timedelta

from homeassistant.util import Throttle
from .const import DOMAIN, ALFEN_PRODUCT_MAP

HEADER_JSON = {'content-type': 'alfen/json; charset=utf-8'}

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)
class AlfenDevice:

    def __init__(self, host, name, session, username, password):
        self.host = host
        self.name = name
        self._status = None
        self._session = session
        self.username = username
        if self.username is None:
            self.username = 'admin'
        self.password = password
    
    async def init(self):
        await self.async_get_info()
        self.id = 'alfen_{}'.format(self.info.identity)
        if self.name is None:
            self.name = f'{self.info.identity} ({self.host})'
        await self.async_update()

    @property
    def status(self):
        return self._status

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return {
            "identifiers": { (DOMAIN, self.id) },
            "manufacturer": "Alfen",
            "model": self.info.model,
            "name": self.name,
            "sw_version": self.info.firmware_version
        }

    def _request(self, parameter_list):
        pass
    
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        await self._do_update()

    async def _do_update(self):
        await self._session.request(ssl=False, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        response = await self._session.request(ssl=False, method='GET', headers = HEADER_JSON, url=self.__get_url('prop?ids=2060_0,2056_0,2221_3,2221_4,2221_5,2221_A,2221_B,2221_C,2221_16,2201_0,2501_2'))

        _LOGGER.debug(f'Status Response {response}')
        self._session.request(ssl=False, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))
        response_json = await response.json(content_type='alfen/json')
        _LOGGER.debug(response_json)

        self._status = AlfenStatus(response_json, self._status)

    async def async_get_info(self):
        response = await self._session.request(ssl=False, method='GET', url=self.__get_url('info'))
        _LOGGER.debug(f'Response {response}')
                
        response_json = await response.json(content_type='alfen/json')
        _LOGGER.debug(response_json)

        self.info = AlfenDeviceInfo(response_json)

    async def reboot_wallbox(self):
        await self._session.request(ssl=False, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        await self._session.post(self.__get_url('cmd'), headers = HEADER_JSON, json={'command': 'reboot'})
        self._session.request(ssl=False, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))

    def __get_url(self, action):
        return 'https://{}/api/{}'.format(self.host, action)

class AlfenStatus:

    def __init__(self,response, prev_status):
        for prop in response['properties']:
            _LOGGER.debug('Prop')
            _LOGGER.debug(prop)

            if prop['id'] == '2060_0':
                self.uptime = max(0, prop['value'] / 1000)
            elif prop['id'] == '2056_0':
                self.bootups = prop['value']
            elif prop['id'] == '2221_3':
                self.voltage_l1 = round(prop['value'], 2)
            elif prop['id'] == '2221_4':
                self.voltage_l2 = round(prop['value'], 2)
            elif prop['id'] == '2221_5':
                self.voltage_l3 = round(prop['value'], 2)
            elif prop['id'] == '2221_A':
                self.current_l1 = round(prop['value'], 2)
            elif prop['id'] == '2221_B':
                self.current_l2 = round(prop['value'], 2)
            elif prop['id'] == '2221_C':
                self.current_l3 = round(prop['value'], 2)          
            elif prop['id'] == '2221_16':
                self.active_power_total = round(prop['value'] / 1000, 2)
            elif prop['id'] == '2201_0':
                self.temperature = round(prop['value'], 2)    
            elif prop['id'] == '2501_2':
                self.status = prop['value'] 
class AlfenDeviceInfo:

    def __init__(self,response):
        self.identity = response['Identity']
        self.firmware_version = response['FWVersion']
        self.model_id = response['Model']

        if ALFEN_PRODUCT_MAP[self.model_id] is None:
            self.model = self.model_id
        else:
            self.model = f'{ALFEN_PRODUCT_MAP[self.model_id]} ({self.model_id})'

        self.object_id = response['ObjectId']
        self.type = response['Type']