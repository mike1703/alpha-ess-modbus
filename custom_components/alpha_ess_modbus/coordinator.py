"""Coordinator polling Alpha ESS registers in merged blocks."""

from datetime import timedelta
import logging

from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BLOCK_GAP_MERGE,
    DOMAIN,
    MANUFACTURER,
    MAX_BLOCK_WORDS,
    REGISTER_SPECS,
)
from .hub import AlphaESSModbusHub, DeviceIdentity

_LOGGER = logging.getLogger(__name__)

CoordinatorData = dict[str, float | int | str | None]


def _merge_blocks(
    specs: tuple, gap: int = BLOCK_GAP_MERGE, max_words: int = MAX_BLOCK_WORDS
) -> list[tuple[int, int]]:
    blocks: list[list[int]] = []
    for spec in sorted(specs, key=lambda s: s.address):
        start = spec.address
        end = spec.address + spec.words - 1
        if (
            blocks
            and start - blocks[-1][1] - 1 <= gap
            and end - blocks[-1][0] + 1 <= max_words
        ):
            blocks[-1][1] = end
        else:
            blocks.append([start, end])
    return [(start, end - start + 1) for start, end in blocks]


class AlphaESSCoordinator(DataUpdateCoordinator[CoordinatorData]):
    """Poll all registers in as few Modbus requests as possible."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        hub: AlphaESSModbusHub,
        identity: DeviceIdentity,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.hub = hub
        self.identity = identity
        self.blocks = _merge_blocks(REGISTER_SPECS)
        _LOGGER.debug("Polling %d register blocks: %s", len(self.blocks), self.blocks)

    @property
    def device_info(self) -> DeviceInfo:
        """Device registry entry describing the inverter system."""
        info = {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": self.config_entry.data.get("name", "Alpha ESS"),
            "manufacturer": MANUFACTURER,
            "model": self.identity.model,
        }
        if self.identity.ems_serial:
            info["serial_number"] = self.identity.ems_serial
        if self.identity.inverter_serial:
            info["hw_version"] = self.identity.inverter_serial
        if self.identity.firmware:
            info["sw_version"] = self.identity.firmware
        return info

    def apply_local_update(self, updates: CoordinatorData) -> None:
        """Optimistically merge values into the stored data after a write."""
        data = dict(self.data or {})
        data.update(updates)
        self.async_set_updated_data(data)

    async def _async_update_data(self) -> CoordinatorData:
        raw: dict[int, int] = {}
        for start, count in self.blocks:
            try:
                words = await self.hub.async_read_words(start, count)
            except (ModbusException, ConnectionError, OSError) as err:
                raise UpdateFailed(f"Error communicating with device: {err}") from err
            raw.update({start + offset: word for offset, word in enumerate(words)})
        return self._parse(raw)

    def _parse(self, raw: dict[int, int]) -> CoordinatorData:
        data: CoordinatorData = {}
        for spec in REGISTER_SPECS:
            try:
                data[spec.key] = self._decode(spec, raw)
            except KeyError:
                data[spec.key] = None
        self._add_derived(data)
        return data

    @staticmethod
    def _decode(spec, raw: dict[int, int]) -> float | int:
        words = [raw[spec.address + offset] for offset in range(spec.words)]
        if spec.dtype == "uint16":
            value: float | int = words[0]
        elif spec.dtype == "int16":
            value = words[0] - 0x10000 if words[0] >= 0x8000 else words[0]
        elif spec.dtype == "uint32":
            value = (words[0] << 16) | words[1]
        else:
            combined = (words[0] << 16) | words[1]
            value = combined - 0x100000000 if combined >= 0x80000000 else combined
        if spec.scale != 1:
            value = value * spec.scale
            if spec.precision is not None:
                value = round(value, spec.precision)
        elif isinstance(value, float):
            value = int(value)
        return value

    @staticmethod
    def _add_derived(data: CoordinatorData) -> None:
        inverter_power = data.get("inverter_power")
        grid_power = data.get("grid_power")
        pv1_power = data.get("pv1_power")
        pv2_power = data.get("pv2_power")
        if inverter_power is not None and grid_power is not None:
            data["house_power"] = inverter_power + grid_power
        if pv1_power is not None:
            data["pv_power"] = pv1_power + (pv2_power or 0)
        pv_energy = data.get("pv_energy_total")
        grid_in = data.get("grid_energy_consume")
        grid_out = data.get("grid_energy_feed")
        if None not in (pv_energy, grid_in, grid_out):
            data["house_energy"] = round(pv_energy + grid_in - grid_out, 2)
