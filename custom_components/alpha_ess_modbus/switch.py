"""Switch platform for the Alpha ESS Modbus integration."""

import logging
from typing import Any

from pymodbus.exceptions import ModbusException

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CHARGE_BLOCK_DURATION,
    DEFAULT_CHARGE_BLOCK_DURATION,
    DISPATCH_MODE_NO_BATTERY_CHARGE,
    DISPATCH_REGISTER_DURATION,
    DISPATCH_REGISTER_MODE,
    DISPATCH_REGISTER_START,
)
from .coordinator import AlphaESSCoordinator
from .entity import AlphaESSEntity

_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTIONS: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="dispatch_control",
        name="Power dispatch",
        icon="mdi:transmission-tower-import",
    ),
    SwitchEntityDescription(
        key="charge_block",
        name="Battery charge block",
        icon="mdi:battery-lock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Alpha ESS switches from a config entry."""
    coordinator: AlphaESSCoordinator = entry.runtime_data
    async_add_entities(
        AlphaESSSwitch(coordinator, description) for description in SWITCH_DESCRIPTIONS
    )


class AlphaESSSwitch(AlphaESSEntity, SwitchEntity):
    """Switches controlling dispatch behaviour."""

    def __init__(
        self,
        coordinator: AlphaESSCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return whether the controlled function is active."""
        if self.coordinator.data is None:
            return None
        active = bool(self.coordinator.data.get("dispatch_active"))
        if self.entity_description.key == "charge_block":
            return (
                active
                and self.coordinator.data.get("dispatch_mode")
                == DISPATCH_MODE_NO_BATTERY_CHARGE
            )
        return active

    async def _async_write_and_refresh(self, updates: dict) -> None:
        await self.coordinator.async_request_refresh()
        self.coordinator.apply_local_update(updates)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the controlled function on the inverter."""
        try:
            if self.entity_description.key == "charge_block":
                duration = self.coordinator.config_entry.options.get(
                    CONF_CHARGE_BLOCK_DURATION, DEFAULT_CHARGE_BLOCK_DURATION
                )
                await self.coordinator.hub.async_write_word(
                    DISPATCH_REGISTER_MODE, DISPATCH_MODE_NO_BATTERY_CHARGE
                )
                await self.coordinator.hub.async_write_uint32(
                    DISPATCH_REGISTER_DURATION, int(duration)
                )
                await self.coordinator.hub.async_write_word(DISPATCH_REGISTER_START, 1)
                await self._async_write_and_refresh(
                    {
                        "dispatch_mode": DISPATCH_MODE_NO_BATTERY_CHARGE,
                        "dispatch_duration": int(duration),
                        "dispatch_active": 1,
                    }
                )
            else:
                await self.coordinator.hub.async_write_word(DISPATCH_REGISTER_START, 1)
                await self._async_write_and_refresh({"dispatch_active": 1})
        except (ModbusException, ConnectionError, OSError) as err:
            _LOGGER.error("Failed to turn on %s: %s", self.entity_description.key, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the dispatch on the inverter."""
        try:
            await self.coordinator.hub.async_write_word(DISPATCH_REGISTER_START, 0)
            await self._async_write_and_refresh({"dispatch_active": 0})
        except (ModbusException, ConnectionError, OSError) as err:
            _LOGGER.error("Failed to turn off %s: %s", self.entity_description.key, err)
