import logging

import voluptuous as vol

from homeassistant.const import (
    CONF_ICON, 
    CONF_NAME, 
    TEMP_CELSIUS)
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
from .const import SERVICE_REBOOT_WALLBOX, ALFEN_STATUS_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up using config_entry."""
    device = hass.data[ALFEN_DOMAIN].get(entry.entry_id)
    async_add_entities([
        AlfenMainSensor(device),
        AlfenSensor(device, 'Status', 'state'),
        AlfenSensor(device, 'Uptime', 'uptime'),
        AlfenSensor(device, 'Bootups', 'bootups'),
        AlfenSensor(device, "Voltage L1", 'voltage_l1', "V"),
        AlfenSensor(device, "Voltage L2", 'voltage_l2', "V"),
        AlfenSensor(device, "Voltage L3", 'voltage_l3', "V"),
        AlfenSensor(device, "Current L1", 'current_l1', "A"),
        AlfenSensor(device, "Current L2", 'current_l2', "A"),
        AlfenSensor(device, "Current L3", 'current_l3', "A"),
        AlfenSensor(device, "Active Power Total", 'active_power_total', "kW"),
        AlfenSensor(device, "Temperature", 'temperature', TEMP_CELSIUS),
    ])

    platform = entity_platform.current_platform.get()

    platform.async_register_entity_service(
        SERVICE_REBOOT_WALLBOX,
        {},
        "reboot_wallbox",
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
        return self._device.status.state

    @property
    def modes(self):
        return [f for f in ALFEN_STATUS_MAP]

    async def async_update(self):
        await self._device.async_update()

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info 
class AlfenSensor(SensorEntity):
    def __init__(self, device: AlfenDevice, name, sensor, unit = None):
        """Initialize the sensor."""
        self._device = device
        self._name = f"{device.name} {name}"
        self._sensor = sensor
        self._unit = unit
        if self._sensor == "active_power_total":
            _LOGGER.info(f'Initiating State sensors {self._name}')
            self._attr_device_class = DEVICE_CLASS_ENERGY


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
        if self._sensor == "current_temperature":
            icon = "mdi:thermometer"
        elif self._sensor == "current_charging_current":
            icon = "mdi:flash"
        elif self._sensor == "current_charging_power":
            icon = "mdi:flash"
        elif self._sensor == "current_limit":
            icon = "mdi:flash"
        elif self._sensor == "pilot_level":
            icon = "mdi:flash"
        elif self._sensor == "acc_session_energy":
            icon = "mdi:flash"
        elif self._sensor == "latest_reading":            
            icon = "mdi:flash"
        elif self._sensor == "latest_reading_k":
            icon = "mdi:flash"
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
        if self._sensor == 'status':
            return self.status_as_str()

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