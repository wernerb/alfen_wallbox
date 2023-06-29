import logging
from typing import Coroutine, Final, Any

from dataclasses import dataclass
from config.custom_components.alfen_wallbox.alfen import AlfenDevice
from config.custom_components.alfen_wallbox.entity import AlfenEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .alfen import AlfenDevice

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)

from homeassistant.core import HomeAssistant, callback
from . import DOMAIN as ALFEN_DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class AlfenSelectDescriptionMixin:
    """Define an entity description mixin for select entities."""

    api_param: str
    options_dict: dict[str, int]


@dataclass
class AlfenSelectDescription(SelectEntityDescription, AlfenSelectDescriptionMixin):
    """Class to describe an Alfen select entity."""


CHARGING_MODE_DICT: Final[dict[str, int]] = {
    "Disable": 0, "Comfort": 1, "Green": 2}


SELECT_TYPES: Final[tuple[AlfenSelectDescription, ...]] = (
    AlfenSelectDescription(
        key="lb_solar_charging_mode",
        name="Solar Charging Mode",
        icon="mdi:solar-power",
        options=list(CHARGING_MODE_DICT),
        options_dict=CHARGING_MODE_DICT,
        api_param="3280_1",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add Alfen Select from a config_entry"""

    device = hass.data[ALFEN_DOMAIN][entry.entry_id]
    async_add_entities([AlfenSelect(device, description)
                       for description in SELECT_TYPES])


class AlfenSelect(AlfenEntity, SelectEntity):
    """Define Alfen select."""

    values_dict: dict[int, str]

    def __init__(self, device: AlfenDevice, description: AlfenSelectDescription) -> None:
        super().__init__(device)
        self._attr_name = f"{description.name}"
        self._attr_options = description.options
        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}_{description.key}"
        self._device = device
        self.values_dict = {v: k for k, v in description.options_dict.items()}

        self._async_update_attrs()

    async def async_select_option(self, option: str) -> None:
        value = {v: k for k, v in self.values_dict.items()}[option]
        await self.update_state(self.entity_description.api_param, value)
        self.async_write_ha_state()

    @property
    def current_option(self) -> str | None:
        return self._get_current_option()

    def _get_current_option(self) -> str | None:
        return getattr(self._device.status, self.entity_description.key)

    async def async_update(self):
        await self._device.async_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update select attributes."""
        self._attr_current_option = self._get_current_option()
