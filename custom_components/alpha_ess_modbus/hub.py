"""Modbus TCP hub for Alpha ESS inverters."""

from dataclasses import dataclass
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    BATTERY_TYPES,
    IDENTITY_EMS_SN_ADDRESS,
    IDENTITY_EMS_SN_WORDS,
    IDENTITY_INV_SN_ADDRESS,
    IDENTITY_INV_SN_WORDS,
    VERSION_FALLBACK_ADDRESS,
    VERSION_PRIMARY_ADDRESS,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class DeviceIdentity:
    """Static identity information read once from the device."""

    ems_serial: str | None = None
    inverter_serial: str | None = None
    firmware: str | None = None
    model: str = "SMILE"


def _words_to_ascii(words: list[int]) -> str:
    raw = b"".join(word.to_bytes(2, byteorder="big") for word in words)
    return "".join(chr(byte) for byte in raw if 32 <= byte < 127).strip()


class AlphaESSModbusHub:
    """Wrapper around an async pymodbus TCP client."""

    def __init__(self, host: str, port: int, slave_id: int) -> None:
        """Initialize the hub."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client = AsyncModbusTcpClient(host=host, port=port, timeout=5)

    async def async_setup(self) -> DeviceIdentity:
        """Connect and read the device identity."""
        if not await self._client.connect():
            raise ConnectionError(
                f"Could not connect to Modbus device at {self._host}:{self._port}"
            )
        return await self.async_read_identity()

    async def async_read_identity(self) -> DeviceIdentity:
        """Read serial numbers, firmware version and battery model."""
        identity = DeviceIdentity()
        try:
            ems_sn = _words_to_ascii(
                await self.async_read_words(
                    IDENTITY_EMS_SN_ADDRESS, IDENTITY_EMS_SN_WORDS
                )
            )
            inv_sn = _words_to_ascii(
                await self.async_read_words(
                    IDENTITY_INV_SN_ADDRESS, IDENTITY_INV_SN_WORDS
                )
            )
            identity.ems_serial = ems_sn or None
            identity.inverter_serial = inv_sn or None

            version = await self._async_read_version(VERSION_PRIMARY_ADDRESS)
            if version is None:
                version = await self._async_read_version(VERSION_FALLBACK_ADDRESS)
            identity.firmware = version

            battery_type = (await self.async_read_words(282, 1))[0]
            if model := BATTERY_TYPES.get(battery_type):
                identity.model = model
        except (ModbusException, ConnectionError, OSError) as err:
            _LOGGER.warning("Could not read full device identity: %s", err)
        return identity

    async def _async_read_version(self, address: int) -> str | None:
        words = await self.async_read_words(address, 3)
        if not any(words):
            return None
        return ".".join(str(word) for word in words)

    async def async_read_words(self, address: int, count: int) -> list[int]:
        """Read holding registers with automatic reconnection."""
        if not self._client.connected and not await self._client.connect():
            raise ConnectionError(f"Not connected to {self._host}:{self._port}")
        result = await self._client.read_holding_registers(
            address=address, count=count, device_id=self._slave_id
        )
        if result.isError():
            raise ModbusException(str(result))
        return list(result.registers)

    async def async_write_word(self, address: int, value: int) -> None:
        """Write a single holding register."""
        if not self._client.connected and not await self._client.connect():
            raise ConnectionError(f"Not connected to {self._host}:{self._port}")
        result = await self._client.write_register(
            address=address, value=value, device_id=self._slave_id
        )
        if result.isError():
            raise ModbusException(str(result))

    async def async_write_words(self, address: int, values: list[int]) -> None:
        """Write consecutive holding registers."""
        if not self._client.connected and not await self._client.connect():
            raise ConnectionError(f"Not connected to {self._host}:{self._port}")
        result = await self._client.write_registers(
            address=address, values=values, device_id=self._slave_id
        )
        if result.isError():
            raise ModbusException(str(result))

    async def async_write_uint32(self, address: int, value: int) -> None:
        """Write a 32 bit value as two big-endian registers."""
        await self.async_write_words(address, [(value >> 16) & 0xFFFF, value & 0xFFFF])

    def async_close(self) -> None:
        """Close the underlying connection."""
        self._client.close()
