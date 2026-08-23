"""Number platform for the Alpha ESS Modbus integration."""

from dataclasses import dataclass
import logging
from typing import Any

from pymodbus.exceptions import ModbusException

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant

from .const import UPS_RESERVE_SOC_MIRROR_ADDRESS
from .coordinator import AlphaESSCoordinator
from .entity import AlphaESSEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AlphaESSNumberDescription(NumberEntityDescription):
    """Number description mapping an entity to writable registers."""

    addresses: tuple[int, ...] = ()
    write_scale: float = 1.0


NUMBER_DESCRIPTIONS: tuple[AlphaESSNumberDescription, ...] = (
    AlphaESSNumberDescription(
        key="ups_reserve_soc",
        name="UPS reserve state of charge",
        device_class=NumberDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=4,
        native_max_value=100,
        native_step=1,
        addresses=(1810, UPS_RESERVE_SOC_MIRROR_ADDRESS),
        write_scale=10,
        icon="mdi:battery-charging-medium",
    ),
    AlphaESSNumberDescription(
        key="max_feed_to_grid",
        name="Max feed to grid",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        addresses=(2048,),
        icon="mdi:solar-power",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Alpha ESS numbers from a config entry."""
    coordinator: AlphaESSCoordinator = entry.runtime_data
    async_add_entities(
        AlphaESSNumber(coordinator, description) for description in NUMBER_DESCRIPTIONS
    )


class AlphaESSNumber(AlphaESSEntity, NumberEntity):
    """Writable setpoint backed by one or more Modbus registers."""

    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: AlphaESSCoordinator,
        description: AlphaESSNumberDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the current register value."""
        value = self.coordinator.data.get(self.entity_description.key)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Write the new setpoint to the inverter."""
        raw = round(value * self.entity_description.write_scale)
        try:
            for address in self.entity_description.addresses:
                await self.coordinator.hub.async_write_word(address, raw)
        except (ModbusException, ConnectionError, OSError) as err:
            _LOGGER.error("Failed to write %s: %s", self.entity_description.key, err)
            return
        self.coordinator.apply_local_update(
            {self.entity_description.key: round(value, 1)}
        )
