"""Sensor platform for the Alpha ESS Modbus integration."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant

from .const import RELAY_MODES, WORK_MODES
from .coordinator import AlphaESSCoordinator
from .entity import AlphaESSEntity


@dataclass(frozen=True, kw_only=True)
class AlphaESSSensorDescription(SensorEntityDescription):
    """Sensor description with enum state mapping support."""

    value_map: dict[int, str] | None = None


SENSOR_DESCRIPTIONS: tuple[AlphaESSSensorDescription, ...] = (
    AlphaESSSensorDescription(
        key="grid_power",
        name="Grid power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="grid_energy_feed",
        name="Grid energy feed-in",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="grid_energy_consume",
        name="Grid energy consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="grid_voltage_a",
        name="Grid voltage phase A",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="grid_voltage_b",
        name="Grid voltage phase B",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="grid_voltage_c",
        name="Grid voltage phase C",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="grid_current_a",
        name="Grid current phase A",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="grid_current_b",
        name="Grid current phase B",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="grid_current_c",
        name="Grid current phase C",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="grid_frequency",
        name="Grid frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="battery_soc",
        name="Battery state of charge",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_voltage",
        name="Battery voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_current",
        name="Battery current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_power",
        name="Battery power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="battery_temp_min",
        name="Minimum cell temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_temp_max",
        name="Maximum cell temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_max_charge_current",
        name="Maximum charge current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_max_discharge_current",
        name="Maximum discharge current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_capacity",
        name="Battery capacity",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_soh",
        name="Battery state of health",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="battery_energy_charge",
        name="Battery charge energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="battery_energy_discharge",
        name="Battery discharge energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="battery_energy_charge_from_grid",
        name="Battery energy charged from grid",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="battery_remaining_time",
        name="Remaining time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="battery_relay_status",
        name="Relay status",
        value_map=RELAY_MODES,
        translation_key="battery_relay_status",
        device_class=SensorDeviceClass.ENUM,
        options=list(RELAY_MODES.values()),
        icon="mdi:electric-switch",
    ),
    AlphaESSSensorDescription(
        key="battery_cell_voltage_min",
        name="Minimum cell voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="battery_cell_voltage_max",
        name="Maximum cell voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="battery_module_count",
        name="Battery module count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="battery_status_raw",
        name="Battery status code",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="battery_warning_raw",
        name="Battery warning bitmap",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-outline",
    ),
    AlphaESSSensorDescription(
        key="battery_fault_raw",
        name="Battery fault bitmap",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-circle-outline",
    ),
    AlphaESSSensorDescription(
        key="pv_power",
        name="PV power total",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="pv_energy_total",
        name="PV energy total",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="pv1_voltage",
        name="PV1 voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="pv1_current",
        name="PV1 current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="pv1_power",
        name="PV1 power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="pv2_voltage",
        name="PV2 voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="pv2_current",
        name="PV2 current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="pv2_power",
        name="PV2 power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="inverter_power",
        name="Inverter power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="inverter_power_l1",
        name="Inverter power L1",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="inverter_voltage_l1",
        name="Inverter voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="inverter_current_l1",
        name="Inverter current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="inverter_frequency",
        name="Inverter frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="inverter_temperature",
        name="Inverter temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    AlphaESSSensorDescription(
        key="inverter_work_mode",
        name="Inverter work mode",
        value_map=WORK_MODES,
        translation_key="inverter_work_mode",
        device_class=SensorDeviceClass.ENUM,
        options=list(WORK_MODES.values()),
        icon="mdi:solar-power-variant",
    ),
    AlphaESSSensorDescription(
        key="backup_power",
        name="Backup power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="backup_power_l1",
        name="Backup power L1",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="backup_voltage_l1",
        name="Backup voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="backup_current_l1",
        name="Backup current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    AlphaESSSensorDescription(
        key="inverter_fault_1",
        name="Inverter fault code 1",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-circle-outline",
    ),
    AlphaESSSensorDescription(
        key="inverter_fault_2",
        name="Inverter fault code 2",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-circle-outline",
    ),
    AlphaESSSensorDescription(
        key="inverter_fault_ext_1",
        name="Inverter extended fault code 1",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-circle-outline",
    ),
    AlphaESSSensorDescription(
        key="inverter_fault_ext_2",
        name="Inverter extended fault code 2",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-circle-outline",
    ),
    AlphaESSSensorDescription(
        key="system_fault_raw",
        name="System fault bitmap",
        entity_category="diagnostic",
        entity_registry_enabled_default=False,
        icon="mdi:alert-circle-outline",
    ),
    AlphaESSSensorDescription(
        key="house_power",
        name="House load power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    AlphaESSSensorDescription(
        key="house_energy",
        name="House load energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
    ),
    AlphaESSSensorDescription(
        key="dispatch_duration",
        name="Dispatch duration",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up Alpha ESS sensors from a config entry."""
    coordinator: AlphaESSCoordinator = entry.runtime_data
    async_add_entities(
        AlphaESSSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class AlphaESSSensor(AlphaESSEntity, SensorEntity):
    """Representation of an Alpha ESS sensor."""

    def __init__(
        self,
        coordinator: AlphaESSCoordinator,
        description: AlphaESSSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float | int | str | None:
        """Return the value reported by the coordinator."""
        value = self.coordinator.data.get(self.entity_description.key)
        if self.entity_description.value_map is not None:
            return (
                self.entity_description.value_map.get(int(value))
                if value is not None
                else None
            )
        return value
