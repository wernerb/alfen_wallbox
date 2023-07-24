from .const import ID, VALUE
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import DOMAIN as ALFEN_DOMAIN
from homeassistant.core import HomeAssistant
import logging
from typing import Final
from dataclasses import dataclass
from .entity import AlfenEntity
from .alfen import AlfenDevice
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfPower,
)


_LOGGER = logging.getLogger(__name__)


@dataclass
class AlfenNumberDescriptionMixin:
    """Define an entity description mixin for select entities."""
    assumed_state: bool
    state: float
    api_param: str
    custom_mode: str


@dataclass
class AlfenNumberDescription(NumberEntityDescription, AlfenNumberDescriptionMixin):
    """Class to describe an Alfen select entity."""


ALFEN_NUMBER_TYPES: Final[tuple[AlfenNumberDescription, ...]] = (
    AlfenNumberDescription(
        key="alb_safe_current",
        name="ALB Safe Current",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.CURRENT,
        native_min_value=1,
        native_max_value=32,
        native_step=1,
        custom_mode=None,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        api_param="2068_0",
    ),
    AlfenNumberDescription(
        key="current_limit",
        name="Current Limit",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.CURRENT,
        native_min_value=0,
        native_max_value=32,
        native_step=1,
        custom_mode=None,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        api_param="2129_0",
    ),
    AlfenNumberDescription(
        key="max_station_current",
        name="Max. Station Current",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.CURRENT,
        native_min_value=0,
        native_max_value=32,
        native_step=1,
        custom_mode=None,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        api_param="2062_0",
    ),
    AlfenNumberDescription(
        key="max_smart_meter_current",
        name="Max. Meter Current",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.CURRENT,
        native_min_value=0,
        native_max_value=32,
        native_step=1,
        custom_mode=None,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        api_param="2067_0",
    ),
    AlfenNumberDescription(
        key="lb_solar_charging_green_share",
        name="Solar Green Share",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.POWER_FACTOR,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        custom_mode=None,
        unit_of_measurement=PERCENTAGE,
        api_param="3280_2",
    ),
    AlfenNumberDescription(
        key="lb_solar_charging_comfort_level",
        name="Solar Comfort Level",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.POWER_FACTOR,
        native_min_value=1400,
        native_max_value=3500,
        native_step=100,
        custom_mode=None,
        unit_of_measurement=UnitOfPower.WATT,
        api_param="3280_3",
    ),
    AlfenNumberDescription(
        key="dp_light_intensity",
        name="Display Light Intensity %",
        state=None,
        icon="mdi:lightbulb",
        assumed_state=False,
        device_class=NumberDeviceClass.POWER_FACTOR,
        native_min_value=0,
        native_max_value=100,
        native_step=10,
        custom_mode=None,
        unit_of_measurement=PERCENTAGE,
        api_param="2061_2",
    ),
    AlfenNumberDescription(
        key="lb_max_imbalance_current",
        name="Max. Imbalance Current between phases",
        state=None,
        icon="mdi:current-ac",
        assumed_state=False,
        device_class=NumberDeviceClass.POWER_FACTOR,
        native_min_value=0,
        native_max_value=10,
        native_step=1,
        custom_mode=None,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        api_param="2174_0",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Alfen select entities from a config entry."""
    device = hass.data[ALFEN_DOMAIN][entry.entry_id]
    numbers = [AlfenNumber(device, description)
               for description in ALFEN_NUMBER_TYPES]

    async_add_entities(numbers)


class AlfenNumber(AlfenEntity, NumberEntity):
    """Define an Alfen select entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(
        self,
        device: AlfenDevice,
        description: AlfenNumberDescription,
    ) -> None:
        """Initialize the Demo Number entity."""
        super().__init__(device)
        self._device = device
        self._attr_name = f"{description.name}"
        self._attr_unique_id = f"{self._device.id}_{description.key}"
        self._attr_assumed_state = description.assumed_state
        self._attr_device_class = description.device_class
        self._attr_icon = description.icon
        if description.custom_mode is None:  # issue with pre Home Assistant Core 2023.6 versions
            self._attr_mode = NumberMode.SLIDER
        else:
            self._attr_mode = description.custom_mode
        self._attr_native_unit_of_measurement = description.unit_of_measurement
        self._attr_native_value = description.state
        self.entity_description = description

        if description.native_min_value is not None:
            self._attr_min_value = description.native_min_value
            self._attr_native_min_value = description.native_min_value
        if description.native_max_value is not None:
            self._attr_max_value = description.native_max_value
            self._attr_native_max_value = description.native_max_value
        if description.native_step is not None:
            self._attr_native_step = description.native_step

    @property
    def native_value(self) -> float | None:
        """Return the entity value to represent the entity state."""
        for prop in self._device.properties:
            if prop[ID] == self.entity_description.api_param:
                return prop[VALUE]
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.update_state(self.entity_description.api_param, int(value))
        self._attr_native_value = self._get_current_option()
        self.async_write_ha_state()

    def _get_current_option(self) -> str | None:
        """Return the current option."""
        for prop in self._device.properties:
            if prop[ID] == self.entity_description.api_param:
                return prop[VALUE]
        return None
