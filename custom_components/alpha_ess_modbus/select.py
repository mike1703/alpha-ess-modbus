"""Select platform for the Alpha ESS Modbus integration."""

import logging
from typing import Any

from pymodbus.exceptions import ModbusException

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DISPATCH_MODE_VALUES, DISPATCH_MODES, DISPATCH_REGISTER_MODE
from .coordinator import AlphaESSCoordinator
from .entity import AlphaESSEntity

_LOGGER = logging.getLogger(__name__)

SELECT_DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key="dispatch_mode",
        name="Dispatch mode",
        translation_key="dispatch_mode",
        options=[state_key for _, state_key in DISPATCH_MODES],
        icon="mdi:cog-transfer-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Alpha ESS selects from a config entry."""
    coordinator: AlphaESSCoordinator = entry.runtime_data
    async_add_entities(
        AlphaESSSelect(coordinator, description) for description in SELECT_DESCRIPTIONS
    )


class AlphaESSSelect(AlphaESSEntity, SelectEntity):
    """Select for the power dispatch mode register."""

    def __init__(
        self,
        coordinator: AlphaESSCoordinator,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        """Return the currently active dispatch mode."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        for raw, state_key in DISPATCH_MODES:
            if raw == int(value):
                return state_key
        return None

    async def async_select_option(self, option: str) -> None:
        """Write the selected dispatch mode to the inverter."""
        raw = DISPATCH_MODE_VALUES.get(option)
        if raw is None:
            _LOGGER.error("Unknown dispatch mode option: %s", option)
            return
        try:
            await self.coordinator.hub.async_write_word(DISPATCH_REGISTER_MODE, raw)
        except (ModbusException, ConnectionError, OSError) as err:
            _LOGGER.error("Failed to write dispatch mode %s: %s", option, err)
            return
        self.coordinator.apply_local_update({"dispatch_mode": raw})
