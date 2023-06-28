import logging

import voluptuous as vol

from homeassistant.const import CONF_ICON, CONF_NAME, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    PLATFORM_SCHEMA,
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)
from homeassistant.helpers import config_validation as cv, entity_platform, service

from . import DOMAIN as ALFEN_DOMAIN

from .alfen import AlfenDevice
from .const import (
    SERVICE_REBOOT_WALLBOX,
    SERVICE_SET_CURRENT_LIMIT,
    SERVICE_ENABLE_RFID_AUTHORIZATION_MODE,
    SERVICE_DISABLE_RFID_AUTHORIZATION_MODE,
    SERVICE_SET_CURRENT_PHASE,
    SERVICE_ENABLE_PHASE_SWITCHING,
    SERVICE_DISABLE_PHASE_SWITCHING,
    SERVICE_SET_GREEN_SHARE,
    SERVICE_SET_COMFORT_POWER,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up using config_entry."""
    device = hass.data[ALFEN_DOMAIN].get(entry.entry_id)
    async_add_entities(
        [
            AlfenMainSensor(device),
            AlfenSensor(device, "Status Code", "status"),
            AlfenSensor(device, "Uptime", "uptime", "s"),
            AlfenSensor(device, "Bootups", "bootups"),
            AlfenSensor(device, "Voltage L1", "voltage_l1", "V"),
            AlfenSensor(device, "Voltage L2", "voltage_l2", "V"),
            AlfenSensor(device, "Voltage L3", "voltage_l3", "V"),
            AlfenSensor(device, "Current L1", "current_l1", "A"),
            AlfenSensor(device, "Current L2", "current_l2", "A"),
            AlfenSensor(device, "Current L3", "current_l3", "A"),
            AlfenSensor(device, "Active Power Total", "active_power_total", "W"),
            AlfenSensor(device, "Meter Reading", "meter_reading", "kWh"),
            AlfenSensor(device, "Temperature", "temperature", TEMP_CELSIUS),
            AlfenSensor(device, "Current Limit", "current_limit", "A"),
            AlfenSensor(device, "Authorization Mode", "auth_mode"),
            AlfenSensor(
                device, "Active Load Balancing Safe Current", "alb_safe_current", "A"
            ),
            AlfenSensor(
                device, "Active Load Balancing Phase Connection", "alb_phase_connection"
            ),
            AlfenSensor(
                device, "Maximum Smart Meter current", "max_station_current", "A"
            ),
            AlfenSensor(device, "Load Balancing Mode", "load_balancing_mode"),
            AlfenSensor(
                device,
                "Main Static Load Balancing Max Current",
                "main_static_lb_max_current",
                "A",
            ),
            AlfenSensor(
                device,
                "Main Active Load Balancing Max Current",
                "main_active_lb_max_current",
                "A",
            ),
            AlfenSensor(device, "Enable Phase Switching", "enable_phase_switching"),
            AlfenSensor(device, "Charging Box Identifier", "charging_box_identifier"),
            AlfenSensor(device, "System Boot Reason", "boot_reason"),
            AlfenSensor(device, "Max Smart Meter Current", "max_smart_meter_current"),
            AlfenSensor(device, "P1 Meter Phase 1 Current", "p1_measurements_1", "A"),
            AlfenSensor(device, "P1 Meter Phase 2 Current", "p1_measurements_2", "A"),
            AlfenSensor(device, "P1 Meter Phase 3 Current", "p1_measurements_3", "A"),
            AlfenSensor(device, "GPRS APN Name", "gprs_apn_name"),
            AlfenSensor(device, "GPRS APN User", "gprs_apn_user"),
            AlfenSensor(device, "GPRS APN Password", "gprs_apn_password"),
            AlfenSensor(device, "GPRS SIM IMSI", "gprs_sim_imsi"),
            AlfenSensor(device, "GPRS SIM Serial", "gprs_sim_iccid"),
            AlfenSensor(device, "GPRS Provider", "gprs_provider"),
            AlfenSensor(
                device,
                "Wired Url Server Domain And Port",
                "comm_bo_url_wired_server_domain_and_port",
            ),
            AlfenSensor(
                device, "Wired Url Wired Server Path", "comm_bo_url_wired_server_path"
            ),
            AlfenSensor(device, "GPRS DHCP Address", "comm_dhcp_address_1"),
            AlfenSensor(device, "GPRS Netmask", "comm_netmask_address_1"),
            AlfenSensor(device, "GPRS Gateway Address", "comm_gateway_address_1"),
            AlfenSensor(device, "GPRS IP Address", "comm_ip_address_1"),
            AlfenSensor(device, "Backoffice Short Name", "comm_bo_short_name"),
            AlfenSensor(
                device,
                "GPRS Url Server Domain And Port",
                "comm_bo_url_gprs_server_domain_and_port",
            ),
            AlfenSensor(device, "GPRS Url Server Path", "comm_bo_url_gprs_server_path"),
            AlfenSensor(device, "GPRS DNS 1", "comm_gprs_dns_1"),
            AlfenSensor(device, "GPRS DNS 2", "comm_gprs_dns_2"),
            AlfenSensor(device, "GPRS Signal", "gprs_signal_strength"),
            AlfenSensor(device, "Wired DHCP", "comm_dhcp_address_2"),
            AlfenSensor(device, "Wired Netmask", "comm_netmask_address_2"),
            AlfenSensor(device, "Wired Gateway Address", "comm_gateway_address_2"),
            AlfenSensor(device, "Wired IP Address", "comm_ip_address_2"),
            AlfenSensor(device, "Wired DNS 1", "comm_wired_dns_1"),
            AlfenSensor(device, "Wired DNS 2", "comm_wired_dns_2"),
            AlfenSensor(device, "Protocol Name", "comm_protocol_name"),
            AlfenSensor(device, "Protocol Version", "comm_protocol_version"),
            AlfenSensor(device, "Solar Charging Mode", "lb_solar_charging_mode"),
            AlfenSensor(
                device,
                "Solar Charging Green Share %",
                "lb_solar_charging_green_share",
                "%",
            ),
            AlfenSensor(
                device,
                "Solar Charging Comfort Level w",
                "lb_solar_charging_comfort_level",
                "W",
            ),
            AlfenSensor(device, "Solar Charging Boost", "lb_solar_charging_boost"),
        ]
    )

    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_REBOOT_WALLBOX,
        {},
        "async_reboot_wallbox",
    )

    platform.async_register_entity_service(
        SERVICE_SET_CURRENT_LIMIT,
        {
            vol.Required("limit"): cv.positive_int,
        },
        "async_set_current_limit",
    )

    platform.async_register_entity_service(
        SERVICE_SET_CURRENT_PHASE,
        {
            vol.Required("phase"): str,
        },
        "async_set_current_phase",
    )

    platform.async_register_entity_service(
        SERVICE_ENABLE_RFID_AUTHORIZATION_MODE,
        {},
        "async_enable_rfid_auth_mode",
    )

    platform.async_register_entity_service(
        SERVICE_DISABLE_RFID_AUTHORIZATION_MODE,
        {},
        "async_disable_rfid_auth_mode",
    )

    platform.async_register_entity_service(
        SERVICE_ENABLE_PHASE_SWITCHING,
        {},
        "async_enable_phase_switching",
    )

    platform.async_register_entity_service(
        SERVICE_DISABLE_PHASE_SWITCHING,
        {},
        "async_disable_phase_switching",
    )

    platform.async_register_entity_service(
        SERVICE_SET_GREEN_SHARE,
        {
            vol.Required("value"): cv.positive_int,
        },
        "async_set_green_share",
    )

    platform.async_register_entity_service(
        SERVICE_SET_COMFORT_POWER,
        {
            vol.Required("value"): cv.positive_int,
        },
        "async_set_comfort_power",
    )


class AlfenMainSensor(Entity):
    def __init__(self, device: AlfenDevice):
        """Initialize the sensor."""
        self._device = device
        self._name = f"{device.name}"
        self._sensor = "sensor"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id}-{self._sensor}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        return "mdi:car-electric"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._device.status is not None:
            return self.status_as_str()
        return None

    async def async_reboot_wallbox(self):
        await self._device.reboot_wallbox()

    async def async_set_current_limit(self, limit):
        await self._device.set_current_limit(limit)

    async def async_enable_rfid_auth_mode(self):
        await self._device.set_rfid_auth_mode(True)

    async def async_disable_rfid_auth_mode(self):
        await self._device.set_rfid_auth_mode(False)

    async def async_update(self):
        await self._device.async_update()

    async def async_set_current_phase(self, phase):
        await self._device.set_current_phase(phase)

    async def async_enable_phase_switching(self):
        await self._device.set_phase_switching(True)

    async def async_disable_phase_switching(self):
        await self._device.set_phase_switching(False)

    async def async_set_green_share(self, value):
        await self._device.set_green_share(value)

    async def async_set_comfort_power(self, value):
        await self._device.set_comfort_power(value)

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info

    def status_as_str(self):
        switcher = {
            0: "Unknown",
            1: "Off",
            2: "Booting",
            3: "Booting Check Mains",
            4: "Available",
            5: "Prep. Authorising",
            6: "Prep. Authorised",
            7: "Prep. Cable connected",
            8: "Prep EV Connected",
            9: "Charging Preparing",
            10: "Vehicle connected",
            11: "Charging Active Normal",
            12: "Charging Active Simplified",
            13: "Charging Suyspended Over Current",
            14: "Charging Suspended HF Switching",
            15: "Charging Suspended EV Disconnected",
            16: "Finish Wait Vehicle",
            17: "Finished Wait Disconnect",
            18: "Error Protective Earth",
            19: "Error Powerline Fault",
            20: "Error Contactor Fault",
            21: "Error Charging",
            22: "Error Power Failure",
            23: "Error Temperature",
            24: "Error Illegal CP Value",
            25: "Error Illegal PP Value",
            26: "Error Too Many Restarts",
            27: "Error",
            28: "Error Message",
            29: "Error Message Not Authorised",
            30: "Error Message Cable Not Supported",
            31: "Error Message S2 Not Opened",
            32: "Error Message Time Out",
            33: "Reserved",
            34: "Inoperative",
            35: "Load Balancing Limited",
            36: "Load Balancing Forced Off",
            38: "Not Charging",
            39: "Solar Charging Wait",
            41: "Solar Charging",
            42: "Charge Point Ready, Waiting For Power",
            43: "Partial Solar Charging",
        }
        return switcher.get(self._device.status.status, "Unknown")


class AlfenSensor(SensorEntity):
    def __init__(self, device: AlfenDevice, name, sensor, unit=None):
        """Initialize the sensor."""
        self._device = device
        self._name = f"{device.name} {name}"
        self._sensor = sensor
        self._unit = unit
        if self._sensor == "active_power_total":
            _LOGGER.info(f"Initiating State sensors {self._name}")
            self._attr_device_class = DEVICE_CLASS_POWER
            self._attr_state_class = STATE_CLASS_MEASUREMENT
        elif self._sensor == "uptime":
            _LOGGER.info(f"Initiating State sensors {self._name}")
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
        elif self._sensor == "meter_reading":
            _LOGGER.info(f"Initiating State sensors {self._name}")
            self._attr_device_class = DEVICE_CLASS_ENERGY
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id}-{self._sensor}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        icon = None
        if self._sensor == "temperature":
            icon = "mdi:thermometer"
        elif (
            (self._sensor.startswith("current_"))
            | (self._sensor.startswith("p1_measurements"))
            | ("_current" in self._sensor)
        ):
            icon = "mdi:current-ac"
        elif self._sensor.startswith("voltage_"):
            icon = "mdi:flash"
        elif self._sensor == "uptime":
            icon = "mdi:timer-outline"
        elif self._sensor == "bootups":
            icon = "mdi:reload"
        elif self._sensor == "active_power_total":
            icon = "mdi:circle-slice-3"
        elif ("gprs_" in self._sensor) | ("_address_1" in self._sensor):
            icon = "mdi:antenna"
        elif ("wired_" in self._sensor) | ("_address_2" in self._sensor):
            icon = "mdi:cable-data"
        elif self._sensor.startswith("lb_solar_charging"):
            icon = "mdi:solar-power"
        return icon

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return round(self.state, 2)

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._sensor in self._device.status.__dict__:
            return self._device.status.__dict__[self._sensor]

    @property
    def unit_of_measurement(self):
        return self._unit

    async def async_update(self):
        await self._device.async_update()

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info
