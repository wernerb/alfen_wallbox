import logging

import requests
import time
import ssl
from enum import Enum
from datetime import timedelta
import datetime

from homeassistant.util import Throttle
from .const import DOMAIN, ALFEN_PRODUCT_MAP

HEADER_JSON = {'content-type': 'alfen/json; charset=utf-8'}
POST_HEADER_JSON = {'content-type': 'application/json'}

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
        # Default ciphers needed as of python 3.10
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.ssl = context        
    
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
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})

        # max 32 ids each time
        response = await self._session.request(
            ssl=self.ssl,
            method='GET',
            headers = HEADER_JSON,
            url=self.__get_url('prop?ids=2060_0,2056_0,2221_3,2221_4,2221_5,2221_A,2221_B,2221_C,2221_16,2201_0,2501_2,2221_22,2129_0,2126_0,2068_0,2069_0,2062_0,2064_0,212B_0,212D_0,2185_0,2053_0,2067_0,212F_1,212F_2,212F_3,2100_0,2101_0,2102_0,2104_0,2105_0'))
        _LOGGER.debug(f'Status Response {response}')

        response2 = await self._session.request(
            ssl=self.ssl,
            method='GET',
            headers = HEADER_JSON,
            url=self.__get_url('prop?ids=2057_0,2112_0,2071_1,2071_2,2072_1,2073_1,2074_1,2075_1,2076_0,2078_1,2078_2,2079_1,2070_2,207A_1,207B_1,207C_1,207D_1,207E_1,207F_1,2080_1,2081_0,2082_0'))
        _LOGGER.debug(f'Status Response {response2}')

        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))

        response_json = await response.json(content_type=None)
        _LOGGER.debug(response_json)

        response_json2 = await response2.json(content_type=None)
        _LOGGER.debug(response_json2)

        response_json_combined = response_json
        
        response_json_combined['properties'] = response_json['properties'] + response_json2['properties']
        response_json_combined['total'] =  response_json['total'] + response_json2['total']
        _LOGGER.debug(response_json2)

        self._status = AlfenStatus(response_json_combined, self._status)

    async def async_get_info(self):
        response = await self._session.request(ssl=self.ssl, method='GET', url=self.__get_url('info'))
        _LOGGER.debug(f'Response {response}')

        if response.status != 200:
            _LOGGER.debug('Info API not available, use generic info')

            generic_info = {
                'Identity': self.host,
                'FWVersion': '?',
                'Model': 'Generic Alfen Wallbox',
                'ObjectId': '?',
                'Type': '?'
            }
            self.info = AlfenDeviceInfo(generic_info)
        else:    
            response_json = await response.json(content_type=None)
            _LOGGER.debug(response_json)

            self.info = AlfenDeviceInfo(response_json)

    async def reboot_wallbox(self):
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        response = await self._session.request(ssl=self.ssl, method='POST', headers = POST_HEADER_JSON, url=self.__get_url('cmd'), json={'command': 'reboot'})
        _LOGGER.debug(f'Reboot response {response}')
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))

    async def set_current_limit(self, limit):
        _LOGGER.debug(f'Set current limit {limit}A')
        if limit > 32 | limit < 1:
            return self.async_abort(reason="invalid_current_limit")

        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        response = await self._session.request(ssl=self.ssl, method='POST', headers = POST_HEADER_JSON, url=self.__get_url('prop'), json={'2129_0': {'id': '2129_0', 'value': limit}})
        _LOGGER.debug(f'Set current limit response {response}')
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))
        await self._do_update()

    async def set_rfid_auth_mode(self, enabled):
        _LOGGER.debug(f'Set RFID Auth Mode {enabled}')

        value = 0
        if enabled:
            value = 2

        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        response = await self._session.request(ssl=self.ssl, method='POST', headers = POST_HEADER_JSON, url=self.__get_url('prop'), json={'2126_0': {'id': '2126_0', 'value': value}})
        _LOGGER.debug(f'Set RFID Auth Mode {response}')
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))
        await self._do_update()        

    async def set_current_phase(self, phase):
        _LOGGER.debug(f'Set current phase {phase}')
        if phase != "L1" and phase != "L2" and phase != "L3":
            return self.async_abort(reason="invalid phase mapping allowed value: L1, L2, L3")
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        response = await self._session.request(ssl=self.ssl, method='POST', headers = POST_HEADER_JSON, url=self.__get_url('prop'), json={'2069_0': {'id': '2069_0', 'value': phase}})
        _LOGGER.debug(f'Set current phase response {response}')
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))
        await self._do_update()

    async def set_phase_switching(self, enabled):
        _LOGGER.debug(f'Set Phase Switching {enabled}')

        value = 0
        if enabled:
            value = 1

        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('login'), json={'username': self.username, 'password': self.password})
        response = await self._session.request(ssl=self.ssl, method='POST', headers = POST_HEADER_JSON, url=self.__get_url('prop'), json={'2185_0': {'id': '2185_0', 'value': value}})
        _LOGGER.debug(f'Set Phase Switching {response}')
        await self._session.request(ssl=self.ssl, method='POST', headers = HEADER_JSON, url=self.__get_url('logout'))
        await self._do_update()

    def __get_url(self, action):
        return 'https://{}/api/{}'.format(self.host, action)

class AlfenStatus:

    def __init__(self,response, prev_status):
        for prop in response['properties']:
            _LOGGER.debug('Prop')
            _LOGGER.debug(prop)

            if prop['id'] == '2060_0':
                self.uptime = max(0, prop['value'] / 1000 * 60)
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
                self.active_power_total = round(prop['value'], 2)
            elif prop['id'] == '2201_0':
                self.temperature = round(prop['value'], 2)    
            elif prop['id'] == '2501_2':
                self.status = prop['value'] 
            elif prop['id'] == '2221_22':
                self.meter_reading = round((prop['value'] / 1000), 2)
            elif prop['id'] == '2129_0':
                self.current_limit = prop['value'] 
            elif prop['id'] == '2126_0':
                self.auth_mode = self.auth_mode_as_str(prop['value']) 
            elif prop['id'] == '2068_0':
                self.alb_safe_current = prop['value']
            elif prop['id'] == '2069_0':
                self.alb_phase_connection = prop['value']
            elif prop['id'] == '2062_0':
                self.max_station_current = prop['value']
            elif prop['id'] == '2064_0':
                self.load_balancing_mode = prop['value']
            elif prop['id'] == '212B_0':
                self.main_static_lb_max_current = round(prop['value'],2)
            elif prop['id'] == '212D_0':
                self.main_active_lb_max_current = round(prop['value'],2)
            elif prop['id'] == '2185_0':
                self.enable_phase_switching = prop['value']
            elif prop['id'] == '2053_0':
                self.charging_box_identifier = prop['value']
            elif prop['id'] == '2057_0':
                self.boot_reason = prop['value']
            elif prop['id'] == '2067_0':
                self.max_smart_meter_current = prop['value']
            elif prop['id'] == '212F_1':
                self.p1_measurements_1 = round(prop['value'], 2)  
            elif prop['id'] == '212F_2':
                self.p1_measurements_2 = round(prop['value'], 2)  
            elif prop['id'] == '212F_3':
                self.p1_measurements_3 = round(prop['value'], 2)  
            elif prop['id'] == '2100_0':
                self.gprs_apn_name = prop['value']
            elif prop['id'] == '2101_0':
                self.gprs_apn_user = prop['value']
            elif prop['id'] == '2102_0':
                self.gprs_apn_password = prop['value']
            elif prop['id'] == '2104_0':
                self.gprs_sim_imsi = prop['value']
            elif prop['id'] == '2105_0':
                self.gprs_sim_iccid = prop['value']
            elif prop['id'] == '2112_0':
                self.gprs_provider = prop['value']
            elif prop['id'] == '2104_0':
                self.p1_measurements_3 = prop['value']
            elif prop['id'] == '2071_1':
                self.comm_bo_url_wired_server_domain_and_port = prop['value']
            elif prop['id'] == '2071_2':
                self.comm_bo_url_wired_server_path = prop['value']
            elif prop['id'] == '2072_1':
                self.comm_dhcp_address_1 = prop['value']
            elif prop['id'] == '2073_1':
                self.comm_netmask_address_1 = prop['value']
            elif prop['id'] == '2074_1':
                self.comm_gateway_address_1 = prop['value']
            elif prop['id'] == '2075_1':
                self.comm_ip_address_1 = prop['value']
            elif prop['id'] == '2076_0':
                self.comm_bo_short_name = prop['value']
            elif prop['id'] == '2078_1':
                self.comm_bo_url_gprs_server_domain_and_port = prop['value']
            elif prop['id'] == '2078_2':
                self.comm_bo_url_gprs_server_path = prop['value']
            elif prop['id'] == '2079_1':
                self.comm_bo_url_gprs_dns_1 = prop['value']
            elif prop['id'] == '207A_1':
                self.comm_dhcp_address_2 = prop['value']
            elif prop['id'] == '207B_1':
                self.comm_netmask_address_2 = prop['value']
            elif prop['id'] == '207C_1':
                self.comm_gateway_address_2 = prop['value']
            elif prop['id'] == '207D_1':
                self.comm_ip_address_2 = prop['value']
            elif prop['id'] == '207E_1':
                self.comm_bo_url_wired_dns_1 = prop['value']
            elif prop['id'] == '207F_1':
                self.comm_bo_url_wired_dns_2 = prop['value']
            elif prop['id'] == '2080_1':
                self.comm_bo_url_gprs_dns_2 = prop['value']
            elif prop['id'] == '2081_0':
                self.comm_protocol_name = prop['value']
            elif prop['id'] == '2082_0':
                self.comm_protocol_version = prop['value']

    def auth_mode_as_str(self, code):
        switcher = {
            0: "Plug and Charge",
            2: "RFID"
        }
        return switcher.get(code, "Unknown")                

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
