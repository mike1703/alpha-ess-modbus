"""Config flow to set up the Alpha ESS Modbus integration."""

from typing import Any

from pymodbus.exceptions import ModbusException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_CHARGE_BLOCK_DURATION,
    CONF_SLAVE_ID,
    DEFAULT_CHARGE_BLOCK_DURATION,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .hub import AlphaESSModbusHub

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("port", default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=247)
        ),
        vol.Optional("name", default=DEFAULT_NAME): str,
    }
)

STEP_OPTIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
        ),
        vol.Required(
            CONF_CHARGE_BLOCK_DURATION, default=DEFAULT_CHARGE_BLOCK_DURATION
        ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
    }
)


async def validate_connection(host: str, port: int, slave_id: int) -> None:
    """Verify the inverter is reachable over Modbus TCP."""
    hub = AlphaESSModbusHub(host=host, port=port, slave_id=slave_id)
    try:
        await hub.async_setup()
    finally:
        hub.async_close()


class AlphaESSModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alpha ESS Modbus."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AlphaESSOptionsFlowHandler:
        """Create the options flow handler."""
        return AlphaESSOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            unique_id = (
                f"{user_input['host']}:{user_input['port']}:{user_input[CONF_SLAVE_ID]}"
            )
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            try:
                await validate_connection(
                    user_input["host"], user_input["port"], user_input[CONF_SLAVE_ID]
                )
            except ConnectionError, OSError, ModbusException:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input["name"], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class AlphaESSOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for the Alpha ESS Modbus integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = STEP_OPTIONS_DATA_SCHEMA
        if current := self.config_entry.options:
            schema = self._inject_defaults(current)
        return self.async_show_form(step_id="init", data_schema=schema)

    def _inject_defaults(self, current: dict[str, Any]) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(
                    "scan_interval",
                    default=current.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
                vol.Required(
                    CONF_CHARGE_BLOCK_DURATION,
                    default=current.get(
                        CONF_CHARGE_BLOCK_DURATION, DEFAULT_CHARGE_BLOCK_DURATION
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
            }
        )
