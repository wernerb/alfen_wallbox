import logging

from dataclasses import dataclass
from typing import Any, Final

from .const import ID, VALUE
from .alfen import AlfenDevice
from .entity import AlfenEntity

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN as ALFEN_DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class AlfenSwitchDescriptionMixin:
    """Define an entity description mixin for binary sensor entities."""

    api_param: str


@dataclass
class AlfenSwitchDescription(SwitchEntityDescription, AlfenSwitchDescriptionMixin):
    """Class to describe an Alfen binary sensor entity."""


ALFEN_BINARY_SENSOR_TYPES: Final[tuple[AlfenSwitchDescription, ...]] = (
    AlfenSwitchDescription(
        key="enable_phase_switching",
        name="Enable Phase Switching",
        api_param="2185_0",
    ),
    AlfenSwitchDescription(
        key="dp_light_auto_dim",
        name="Display Light Auto Dim",
        api_param="2061_1",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alfen switch entities from a config entry."""
    device = hass.data[ALFEN_DOMAIN][entry.entry_id]
    switches = [AlfenSwitchSensor(device, description)
                for description in ALFEN_BINARY_SENSOR_TYPES]

    async_add_entities(switches)


class AlfenSwitchSensor(AlfenEntity, SwitchEntity):
    """Define an Alfen binary sensor."""

    def __init__(self,
                 device: AlfenDevice,
                 description: AlfenSwitchDescription
                 ) -> None:
        """Initialize."""
        super().__init__(device)
        self._device = device
        self._attr_name = f"{device.name} {description.name}"
        self._attr_unique_id = f"{self._device.id}_{description.key}"
        self.entity_description = description

    @property
    def available(self) -> bool:
        for prop in self._device.properties:
            if prop[ID] == self.entity_description.api_param:
                return True
        return False

    @property
    def is_on(self) -> bool:
        for prop in self._device.properties:
            if prop[ID] == self.entity_description.api_param:
                return prop[VALUE] == 1

        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        # Do the turning on.
        await self.update_state(self.entity_description.api_param, 1)
        await self._device.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.update_state(self.entity_description.api_param, 0)
        await self._device.async_update()
