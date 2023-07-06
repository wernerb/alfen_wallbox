import logging
from typing import Final, Any

from dataclasses import dataclass
from .entity import AlfenEntity

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

ON_OFF_DICT: Final[dict[str, int]] = {"Off": 0, "On": 1}

PHASE_ROTATION_DICT: Final[dict[str, str]] = {
    "L1": "L1",
    "L2": "L2",
    "L3": "L3",
    "L1,L2,L3": "L1L2L3",
    "L1,L3,L2": "L1L3L2",
    "L2,L1,L3": "L2L1L3",
    "L2,L3,L1": "L2L3L1",
    "L3,L1,L2": "L3L1L2",
    "L3,L2,L1": "L3L2L1",
}

SAFE_AMPS_DICT: Final[dict[str, int]] = {
    "1 A": 1,
    "2 A": 2,
    "3 A": 3,
    "4 A": 4,
    "5 A": 5,
    "6 A": 6,
    "7 A": 7,
    "8 A": 8,
    "9 A": 9,
    "10 A": 10,
}

AUTH_MODE_DICT: Final[dict[str, int]] = {
    "Plug and Charge": 0,
    "RFID": 2
}

LOAD_BALANCE_MODE_DICT: Final[dict[str, int]] = {
    "Modbus TCP/IP": 0,
    "DSMR4.x / SMR5.0 (P1)": 3
}

LOAD_BALANCE_DATA_SOURCE_DICT: Final[dict[str, int]] = {
    "Meter": 0,
    "Energy Management System": 3
}

LOAD_BALANCE_RECEIVED_MEASUREMENTS_DICT: Final[dict[str, int]] = {
    "Exclude Charging Ev": 0,
    "Include Charging Ev": 1
}

DISPLAY_LANGUAGE_DICT: Final[dict[str, str]] = {
    "English": "en_GB",
    "Dutch": "nl_NL",
    "German": "de_DE",
    "French": "fr_FR",
    "Italian": "it_IT",
    "Norwegian": "no_NO",
    "Finnish": "fi_FI",
    "Portuguese": "pt_PT",
    "Spanish": "es_ES",
    "Swedish": "sv_SE",
}

ALLOWED_PHASE_DICT: Final[dict[str, int]] = {
    "1 Phase": 1,
    "3 Phases": 3,
}

PRIORITIES_DICT: Final[dict[str, int]] = {
    "Disable": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4
}

OPERATIVE_MODE_DICT: Final[dict[str, int]] = {
    "Operative": 0,
    "In-operative": 2,
}

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
        key="lb_solar_charging_boost",
        name="Solar Charging Boost",
        icon="mdi:ev-station",
        options=list(ON_OFF_DICT),
        options_dict=ON_OFF_DICT,
        api_param="3280_4",
    ),
    AlfenSelectDescription(
        key="alb_phase_connection",
        name="Active Load Balancing Phase Connection",
        icon=None,
        options=list(PHASE_ROTATION_DICT),
        options_dict=PHASE_ROTATION_DICT,
        api_param="2069_0",
    ),
    # AlfenSelectDescription(
    #     key="alb_safe_current",
    #     name="Active Load Balancing Safe Current",
    #     icon="mdi:current-ac",
    #     options=list(SAFE_AMPS_DICT),
    #     options_dict=SAFE_AMPS_DICT,
    #     api_param="2068_0",
    # ),

    AlfenSelectDescription(
        key="auth_mode",
        name="Authorization Mode",
        icon="mdi:key",
        options=list(AUTH_MODE_DICT),
        options_dict=AUTH_MODE_DICT,
        api_param="2126_0",
    ),

    AlfenSelectDescription(
        key="load_balancing_mode",
        name="Load Balancing Mode",
        icon="mdi:scale-balance",
        options=list(LOAD_BALANCE_MODE_DICT),
        options_dict=LOAD_BALANCE_MODE_DICT,
        api_param="2064_0",
    ),
    AlfenSelectDescription(
        key="lb_active_balancing_received_measurements",
        name="Load Balancing Received Measurements",
        icon="mdi:scale-balance",
        options=list(LOAD_BALANCE_RECEIVED_MEASUREMENTS_DICT),
        options_dict=LOAD_BALANCE_RECEIVED_MEASUREMENTS_DICT,
        api_param="206F_0",
    ),
    AlfenSelectDescription(
        key="display_language",
        name="Display Language",
        icon="mdi:translate",
        options=list(DISPLAY_LANGUAGE_DICT),
        options_dict=DISPLAY_LANGUAGE_DICT,
        api_param="205D_0",
    ),
    AlfenSelectDescription(
        key="bo_network_1_connection_priority",
        name="Backoffice Network 1 Connection Priority (Ethernet)",
        icon="mdi:ethernet-cable",
        options=list(PRIORITIES_DICT),
        options_dict=PRIORITIES_DICT,
        api_param="20F0_E",
    ),
    AlfenSelectDescription(
        key="bo_network_2_connection_priority",
        name="Backoffice Network 2 Connection Priority (GPRS)",
        icon="mdi:antenna",
        options=list(PRIORITIES_DICT),
        options_dict=PRIORITIES_DICT,
        api_param="20F1_E",
    ),
    AlfenSelectDescription(
        key="socket_1_operation_mode",
        name="Socket 1 Operation Mode",
        icon="mdi:power-socket-eu",
        options=list(OPERATIVE_MODE_DICT),
        options_dict=OPERATIVE_MODE_DICT,
        api_param="205F_0",
    ),





)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add Alfen Select from a config_entry"""

    device = hass.data[ALFEN_DOMAIN][entry.entry_id]
    selects = [AlfenSelect(device, description)
               for description in ALFEN_SELECT_TYPES]

    async_add_entities(selects)


class AlfenSelect(AlfenEntity, SelectEntity):
    """Define Alfen select."""

    values_dict: dict[int, str]

    def __init__(
        self, device: AlfenDevice, description: AlfenSelectDescription
    ) -> None:
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
            if prop["id"] == self.entity_description.api_param:
                return prop["value"]
        return None

    async def async_update(self):
        """Update the entity."""
        await self._device.async_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update select attributes."""
        self._attr_current_option = self._get_current_option()
