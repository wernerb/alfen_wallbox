"""Alfen Wallbox integration."""

import asyncio
from datetime import timedelta
import logging

from aiohttp import ClientConnectionError
from async_timeout import timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .alfen import AlfenDevice

from .const import (
    DOMAIN,
    TIMEOUT,
)

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.TEXT
]
SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Alfen Wallbox component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    conf = entry.data
    device = await alfen_setup(
        hass, conf[CONF_HOST], conf[CONF_NAME], conf[CONF_USERNAME], conf[CONF_PASSWORD]
    )
    if not device:
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = device

    # hass.data.setdefault(DOMAIN, {}).update({entry.entry_id: device})

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("async_unload_entry: %s", config_entry)

    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    hass.data[DOMAIN].pop(config_entry.entry_id)
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    return unload_ok


async def alfen_setup(hass: HomeAssistant, host: str, name: str, username: str, password: str) -> AlfenDevice | None:
    """Create a Alfen instance only once."""

    session = async_get_clientsession(hass, verify_ssl=False)
    try:
        with timeout(TIMEOUT):
            device = AlfenDevice(host, name, session, username, password)
            await device.init()
    except asyncio.TimeoutError:
        _LOGGER.debug("Connection to %s timed out", host)
        raise ConfigEntryNotReady
    except ClientConnectionError:
        _LOGGER.debug("ClientConnectionError to %s", host)
        raise ConfigEntryNotReady
    except Exception:  # pylint: disable=broad-except
        _LOGGER.error("Unexpected error creating device %s", host)
        return None

    return device
