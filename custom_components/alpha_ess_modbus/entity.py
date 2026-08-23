"""Shared entity base classes for the Alpha ESS Modbus integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AlphaESSCoordinator


class AlphaESSEntity(CoordinatorEntity[AlphaESSCoordinator], Entity):
    """Base entity wired to the coordinator and the device registry."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AlphaESSCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(**coordinator.device_info)

    @property
    def available(self) -> bool:
        """Return whether the last coordinator update succeeded."""
        return self.coordinator.last_update_success
