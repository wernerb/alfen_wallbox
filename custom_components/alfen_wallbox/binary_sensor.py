import logging

from dataclasses import dataclass
from typing import Final
from config.custom_components.alfen_wallbox.alfen import AlfenDevice
from config.custom_components.alfen_wallbox.entity import AlfenEntity

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN as ALFEN_DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class AlfenBinaryDescriptionMixin:
    """Define an entity description mixin for binary sensor entities."""

    api_param: str


@dataclass
class AlfenBinaryDescription(BinarySensorEntityDescription, AlfenBinaryDescriptionMixin):
    """Class to describe an Alfen binary sensor entity."""


ALFEN_BINARY_SENSOR_TYPES: Final[tuple[AlfenBinaryDescription, ...]] = (
    AlfenBinaryDescription(
        key="system_date_light_savings",
        name="System Daylight Savings",
        device_class=None,
        api_param="205B_0",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alfen binary sensor entities from a config entry."""
    device = hass.data[ALFEN_DOMAIN][entry.entry_id]
    binaries = [AlfenBinarySensor(device, description)
                for description in ALFEN_BINARY_SENSOR_TYPES]

    async_add_entities(binaries)


class AlfenBinarySensor(AlfenEntity, BinarySensorEntity):
    """Define an Alfen binary sensor."""

    # entity_description: AlfenBinaryDescriptionMixin

    def __init__(self,
                 device: AlfenDevice,
                 description: AlfenBinaryDescription
                 ) -> None:
        """Initialize."""
        super().__init__(device)
        self._device = device
        self._attr_name = f"{device.name} {description.name}"
        self._attr_unique_id = f"{self._attr_unique_id}_{description.key}"
        self.entity_description = description

    @property
    def available(self) -> bool:
        for prop in self._device.properties:
            if prop["id"] == self.entity_description.api_param:
                return True
        return False

    @property
    def is_on(self) -> bool:
        for prop in self._device.properties:
            if prop["id"] == self.entity_description.api_param:
                return prop["value"] == 1

        return False
