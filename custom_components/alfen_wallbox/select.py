import logging
from typing import Final, Any

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

ON_OFF_DICT: Final[dict[str, int]] = {
    "Off": 0, "On": 1}

ALFEN_SELECT_TYPES: Final[tuple[AlfenSelectDescription, ...]] = (
    AlfenSelectDescription(
        key="lb_solar_charging_mode",
        name="Solar Charging Mode",
        icon="mdi:solar-power",
        options=list(CHARGING_MODE_DICT),
        options_dict=CHARGING_MODE_DICT,
        api_param="3280_1",
    ),
    AlfenSelectDescription(
        key="enable_phase_switching",
        name="Enable Phase Switching",
        icon="mdi:ev-station",
        options=list(ON_OFF_DICT),
        options_dict=ON_OFF_DICT,
        api_param="2185_0",
    ),
    AlfenSelectDescription(
        key="lb_solar_charging_boost",
        name="Solar Charging Boost",
        icon="mdi:ev-station",
        options=list(ON_OFF_DICT),
        options_dict=ON_OFF_DICT,
        api_param="3280_4",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Add Alfen Select from a config_entry"""

    device = hass.data[ALFEN_DOMAIN][entry.entry_id]
    selects = [
        AlfenSelect(device, description) for description in ALFEN_SELECT_TYPES
    ]

    async_add_entities(selects)


class AlfenSelect(AlfenEntity, SelectEntity):
    """Define Alfen select."""

    values_dict: dict[int, str]

    def __init__(self,
                 device: AlfenDevice,
                 description: AlfenSelectDescription) -> None:
        """Initialize."""
        super().__init__(device)
        self._device = device
        self._attr_name = f"{device.name} {description.name}"

        self._attr_unique_id = f"{self._attr_unique_id}_{description.key}"
        self._attr_options = description.options
        self.entity_description = description
        self.values_dict = {v: k for k, v in description.options_dict.items()}
        self._async_update_attrs()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = {v: k for k, v in self.values_dict.items()}[option]
        await self.update_state(self.entity_description.api_param, value)
        self.async_write_ha_state()

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        value = self._get_current_option()
        return self.values_dict.get(value)

    def _get_current_option(self) -> str | None:
        """Return the current option."""
        for prop in self._device.properties:
            if prop['id'] == self.entity_description.api_param:
                return prop['value']
        return None

    async def async_update(self):
        """Update the entity."""
        await self._device.async_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update select attributes."""
        self._attr_current_option = self._get_current_option()
