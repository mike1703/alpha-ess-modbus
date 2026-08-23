"""Test the Alpha ESS Modbus config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.alpha_ess_modbus.const import DOMAIN

CONFIG_INPUT = {
    "host": "192.168.1.100",
    "port": 502,
    "slave_id": 85,
    "name": "Alpha ESS",
}


async def test_user_form_creates_entry(hass: HomeAssistant) -> None:
    """A valid connection finishes the flow and creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with (
        patch(
            "custom_components.alpha_ess_modbus.config_flow.validate_connection",
            new_callable=AsyncMock,
        ),
        patch(
            "custom_components.alpha_ess_modbus.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == CONFIG_INPUT
    assert len(mock_setup_entry.mock_calls) == 1


async def test_cannot_connect_shows_error(hass: HomeAssistant) -> None:
    """A failed connection redisplays the form with an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.alpha_ess_modbus.config_flow.validate_connection",
        side_effect=ConnectionError("nope"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_INPUT
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_duplicate_host_aborts(hass: HomeAssistant) -> None:
    """Configuring the same host twice is aborted."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="192.168.1.100:502:85",
        data=CONFIG_INPUT,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.alpha_ess_modbus.config_flow.validate_connection",
        new_callable=AsyncMock,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], CONFIG_INPUT
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
