"""The Alpha ESS Modbus integration."""

import logging

from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_SLAVE_ID, DEFAULT_SCAN_INTERVAL
from .coordinator import AlphaESSCoordinator
from .hub import AlphaESSModbusHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

type AlphaESSConfigEntry = ConfigEntry[AlphaESSCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AlphaESSConfigEntry) -> bool:
    """Set up Alpha ESS Modbus from a config entry."""
    hub = AlphaESSModbusHub(
        host=entry.data["host"],
        port=entry.data["port"],
        slave_id=entry.data[CONF_SLAVE_ID],
    )
    try:
        identity = await hub.async_setup()
    except (ConnectionError, OSError, ModbusException) as err:
        hub.async_close()
        raise ConfigEntryNotReady(f"Could not connect to {entry.data['host']}") from err

    coordinator = AlphaESSCoordinator(
        hass,
        entry,
        hub,
        identity,
        scan_interval=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AlphaESSConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: AlphaESSCoordinator = entry.runtime_data
        coordinator.hub.async_close()
    return unload_ok


async def async_update_listener(
    hass: HomeAssistant, entry: AlphaESSConfigEntry
) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
