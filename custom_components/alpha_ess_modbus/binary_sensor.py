"""Binary sensor platform for the Alpha ESS Modbus integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import WORK_MODES
from .coordinator import AlphaESSCoordinator
from .entity import AlphaESSEntity


@dataclass(frozen=True, kw_only=True)
class AlphaESSBinarySensorDescription(BinarySensorEntityDescription):
    """Binary sensor description with a value function."""

    value_fn: Callable[[dict], bool]


BINARY_SENSOR_DESCRIPTIONS: tuple[AlphaESSBinarySensorDescription, ...] = (
    AlphaESSBinarySensorDescription(
        key="exporting_to_grid",
        name="Exporting to grid",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=lambda data: (data.get("grid_power") or 0) < 0,
    ),
    AlphaESSBinarySensorDescription(
        key="importing_from_grid",
        name="Importing from grid",
        device_class=BinarySensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        value_fn=lambda data: (data.get("grid_power") or 0) > 0,
    ),
    AlphaESSBinarySensorDescription(
        key="battery_charging",
        name="Battery charging",
        icon="mdi:battery-arrow-up",
        value_fn=lambda data: (data.get("battery_power") or 0) < 0,
    ),
    AlphaESSBinarySensorDescription(
        key="battery_discharging",
        name="Battery discharging",
        icon="mdi:battery-arrow-down",
        entity_registry_enabled_default=False,
        value_fn=lambda data: (data.get("battery_power") or 0) > 0,
    ),
    AlphaESSBinarySensorDescription(
        key="system_fault",
        name="System fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: any(
            data.get(key)
            for key in (
                "system_fault_raw",
                "battery_fault_raw",
                "inverter_fault_1",
                "inverter_fault_2",
            )
        ),
    ),
    AlphaESSBinarySensorDescription(
        key="inverter_online",
        name="Inverter online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: data.get("inverter_work_mode") == WORK_MODES.get(1),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Alpha ESS binary sensors from a config entry."""
    coordinator: AlphaESSCoordinator = entry.runtime_data
    async_add_entities(
        AlphaESSBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class AlphaESSBinarySensor(AlphaESSEntity, BinarySensorEntity):
    """Representation of an Alpha ESS binary sensor."""

    def __init__(
        self,
        coordinator: AlphaESSCoordinator,
        description: AlphaESSBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the state computed from coordinator data."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
