"""Constants for the Alpha ESS Modbus integration."""

from dataclasses import dataclass
from typing import Final

DOMAIN: Final = "alpha_ess_modbus"
MANUFACTURER: Final = "Alpha ESS"

CONF_SLAVE_ID: Final = "slave_id"
CONF_CHARGE_BLOCK_DURATION: Final = "charge_block_duration"

DEFAULT_NAME: Final = "Alpha ESS"
DEFAULT_PORT: Final = 502
DEFAULT_SLAVE_ID: Final = 85
DEFAULT_SCAN_INTERVAL: Final = 10
DEFAULT_CHARGE_BLOCK_DURATION: Final = 3600

MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 600

MAX_BLOCK_WORDS: Final = 100
BLOCK_GAP_MERGE: Final = 12


@dataclass(frozen=True, slots=True)
class RegisterSpec:
    """Specification of a polled Modbus holding register value."""

    key: str
    address: int
    words: int = 1
    dtype: str = "uint16"
    scale: float = 1.0
    precision: int | None = None


REGISTER_SPECS: Final[tuple[RegisterSpec, ...]] = (
    RegisterSpec("grid_energy_feed", 16, words=2, dtype="uint32", scale=0.01),
    RegisterSpec("grid_energy_consume", 18, words=2, dtype="uint32", scale=0.01),
    RegisterSpec("grid_voltage_a", 20),
    RegisterSpec("grid_voltage_b", 21),
    RegisterSpec("grid_voltage_c", 22),
    RegisterSpec("grid_current_a", 23, dtype="int16", scale=0.1),
    RegisterSpec("grid_current_b", 24, dtype="int16", scale=0.1),
    RegisterSpec("grid_current_c", 25, dtype="int16", scale=0.1),
    RegisterSpec("grid_frequency", 26, scale=0.01),
    RegisterSpec("grid_power", 33, words=2, dtype="int32"),
    RegisterSpec("battery_voltage", 256, dtype="int16", scale=0.1),
    RegisterSpec("battery_current", 257, dtype="int16", scale=0.1),
    RegisterSpec("battery_soc", 258, dtype="int16", scale=0.1),
    RegisterSpec("battery_status_raw", 259),
    RegisterSpec("battery_relay_status", 260),
    RegisterSpec("battery_cell_voltage_min", 263, scale=0.001),
    RegisterSpec("battery_cell_voltage_max", 266, scale=0.001),
    RegisterSpec("battery_temp_min", 269, dtype="int16", scale=0.1),
    RegisterSpec("battery_temp_max", 272, dtype="int16", scale=0.1),
    RegisterSpec("battery_max_charge_current", 273, scale=0.1),
    RegisterSpec("battery_max_discharge_current", 274, scale=0.1),
    RegisterSpec("battery_module_count", 280),
    RegisterSpec("battery_capacity", 281, scale=0.1),
    RegisterSpec("battery_type_raw", 282),
    RegisterSpec("battery_soh", 283, scale=0.1),
    RegisterSpec("battery_warning_raw", 284, words=2, dtype="uint32"),
    RegisterSpec("battery_fault_raw", 286, words=2, dtype="uint32"),
    RegisterSpec(
        "battery_energy_charge", 288, words=2, dtype="uint32", scale=0.1, precision=2
    ),
    RegisterSpec(
        "battery_energy_discharge", 290, words=2, dtype="uint32", scale=0.1, precision=2
    ),
    RegisterSpec(
        "battery_energy_charge_from_grid",
        292,
        words=2,
        dtype="uint32",
        scale=0.1,
        precision=2,
    ),
    RegisterSpec("battery_power", 294, dtype="int16"),
    RegisterSpec("battery_remaining_time", 295),
    RegisterSpec("inverter_voltage_l1", 1024, scale=0.1),
    RegisterSpec("inverter_current_l1", 1027, dtype="int16", scale=0.1),
    RegisterSpec("inverter_power_l1", 1030, words=2, dtype="int32"),
    RegisterSpec("inverter_power", 1036, words=2, dtype="int32"),
    RegisterSpec("backup_voltage_l1", 1038, scale=0.1),
    RegisterSpec("backup_current_l1", 1041, scale=0.1),
    RegisterSpec("backup_power_l1", 1044, words=2, dtype="uint32"),
    RegisterSpec("backup_power", 1050, words=2, dtype="uint32"),
    RegisterSpec("inverter_frequency", 1052, scale=0.01),
    RegisterSpec("pv1_voltage", 1053, scale=0.1),
    RegisterSpec("pv1_current", 1054, scale=0.1),
    RegisterSpec("pv1_power", 1055, words=2, dtype="uint32"),
    RegisterSpec("pv2_voltage", 1057, scale=0.1),
    RegisterSpec("pv2_current", 1058, scale=0.1),
    RegisterSpec("pv2_power", 1059, words=2, dtype="uint32"),
    RegisterSpec("inverter_temperature", 1077, dtype="int16", scale=0.1),
    RegisterSpec("inverter_fault_1", 1082, words=2, dtype="uint32"),
    RegisterSpec("inverter_fault_2", 1084, words=2, dtype="uint32"),
    RegisterSpec("pv_energy_total", 1086, words=2, dtype="uint32", scale=0.1),
    RegisterSpec("inverter_work_mode", 1088),
    RegisterSpec("inverter_fault_ext_1", 1099, words=2, dtype="uint32"),
    RegisterSpec("inverter_fault_ext_2", 1101, words=2, dtype="uint32"),
    RegisterSpec("system_fault_raw", 1793, words=2, dtype="uint32"),
    RegisterSpec("ups_reserve_soc", 1810, scale=0.1),
    RegisterSpec("max_feed_to_grid", 2048),
    RegisterSpec("dispatch_active", 2176),
    RegisterSpec("dispatch_mode", 2181),
    RegisterSpec("dispatch_duration", 2183, words=2, dtype="uint32"),
)

REGISTER_SPECS_BY_KEY: Final[dict[str, RegisterSpec]] = {
    spec.key: spec for spec in REGISTER_SPECS
}

IDENTITY_EMS_SN_ADDRESS: Final = 1859
IDENTITY_EMS_SN_WORDS: Final = 8
IDENTITY_INV_SN_ADDRESS: Final = 1610
IDENTITY_INV_SN_WORDS: Final = 10
VERSION_PRIMARY_ADDRESS: Final = 1867
VERSION_FALLBACK_ADDRESS: Final = 1833

BATTERY_TYPES: Final[dict[int, str]] = {
    2: "M4860",
    3: "M48100",
    13: "48112-P",
    16: "SMILE5-BAT",
    24: "M4856-P",
    27: "Smile-BAT-10.3P",
    30: "Smile-BAT-10.1P",
    33: "Smile-BAT-5.8P",
    34: "Smile-BAT5-JP",
    35: "Smile-BAT-13.7P",
}

WORK_MODES: Final[dict[int, str]] = {
    0: "wait",
    1: "online",
    2: "ups",
    3: "bypass",
    4: "fault",
    5: "dc",
    6: "selftest",
    7: "check",
    8: "update_master",
    9: "update_slave",
    10: "update_arm",
}

RELAY_MODES: Final[dict[int, str]] = {
    0: "disconnected",
    1: "discharge_only",
    2: "charge_only",
    3: "both",
}

DISPATCH_MODES: Final[tuple[tuple[int, str], ...]] = (
    (1, "battery_pv_only"),
    (2, "soc_control"),
    (3, "load_following"),
    (4, "maximise_output"),
    (5, "normal"),
    (6, "optimise_consumption"),
    (7, "maximise_consumption"),
    (8, "eco"),
    (10, "pv_power_setting"),
    (19, "no_battery_charge"),
)

DISPATCH_MODE_VALUES: Final[dict[str, int]] = {
    state_key: value for value, state_key in DISPATCH_MODES
}

DISPATCH_MODE_NO_BATTERY_CHARGE: Final = 19
DISPATCH_REGISTER_START: Final = 2176
DISPATCH_REGISTER_MODE: Final = 2181
DISPATCH_REGISTER_DURATION: Final = 2183
UPS_RESERVE_SOC_MIRROR_ADDRESS: Final = 2128
