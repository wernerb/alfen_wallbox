"""Base entity for Alfen Wallbox integration."""
import logging

from homeassistant.helpers.entity import DeviceInfo, Entity

from .alfen import AlfenDevice
from .const import DOMAIN as ALFEN_DOMAIN

_LOGGER = logging.getLogger(__name__)


class AlfenEntity(Entity):
    """Define a base Alfen entity."""

    def __init__(self, device: AlfenDevice) -> None:
        """Initialize the Alfen entity."""
        self._device = device

        self._attr_device_info = DeviceInfo(
            identifiers={(ALFEN_DOMAIN, self._device.name)},
            manufacturer="Alfen",
            model=self._device.info.model,
            name=device.name,
            sw_version=self._device.info.firmware_version,
        )

    async def async_added_to_hass(self) -> None:
        """Add listener for state changes."""
        await super().async_added_to_hass()
