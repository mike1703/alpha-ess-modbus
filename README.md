# Alpha ESS Modbus for Home Assistant

A native Home Assistant integration for Alpha ESS battery storage systems, communicating directly over local **Modbus TCP**. All values are exposed as entities of a single, proper Home Assistant device — no YAML `modbus:` blocks, helpers or automations required.

Built from the official Alpha ESS *Household Register parameter list* and field-tested against a **SMILE-G3-S5** hybrid inverter with **SMILE-G3-BAT-3.8S** batteries and a Backup Box Plus.

## Supported features

- UI-based setup (config flow) with connection validation
- Single device entry with serial number (EMS SN), hardware version (inverter SN) and firmware version read from the device
- Efficient register polling: contiguous register ranges are merged into block reads (~8 requests per update instead of one per sensor)
- ~50 sensors incl. computed house-load power/energy and PV totals
- Binary sensors for grid import/export, battery charging/discharging, faults and inverter availability
- Writable setpoints (number entities): UPS reserve state of charge, max feed-to-grid percentage
- Dispatch control: select the dispatch mode and start/stop it via switch
- Battery charge-block switch (equivalent to writing dispatch mode 19 "No Battery Charge" with a configurable duration)
- English and German translations, enum states rendered as translated labels
- Configurable poll interval and charge-block duration via the options flow

### Supported hardware

Any Alpha ESS household system exposing the documented Modbus holding-register interface over TCP, e.g.:

- SMILE-G3 series (SMILE-G3-S5, G3-S3.6, G3-B5, …)
- SMILE-S5 / SMILE5
- Other SMILE household inverters sharing the same register map

> The Modbus TCP server must be enabled on the inverter (default port `502`, default slave ID `85` / `0x55`). Consult the Alpha ESS Modbus documentation for your firmware on how to enable it.

## Installation

1. Copy the folder `custom_components/alpha_ess_modbus` into your Home Assistant configuration directory, so that you end up with `<config>/custom_components/alpha_ess_modbus/`.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **Alpha ESS Modbus**.
4. Enter host/IP, port (`502`), Modbus slave ID (`85`) and an optional name.

## Configuration options

Available via **Configure** on the integration card:

| Option | Default | Description |
| --- | --- | --- |
| Poll interval | 10 s | How often registers are read (5–600 s) |
| Charge block duration | 3600 s | Duration written to the dispatch timer when enabling the charge-block switch |

## Entities

### Sensors

| Entity | Register(s) | Unit | Notes |
| --- | --- | --- | --- |
| Grid power | 33–34 (int32) | W | Positive = import from grid |
| Grid energy feed-in | 16–17 (uint32) | kWh | Total increasing |
| Grid energy consumption | 18–19 (uint32) | kWh | Total increasing |
| Grid voltage phase A / B / C | 20 / 21 / 22 | V | B/C disabled by default |
| Grid current phase A / B / C | 23 / 24 / 25 | A | B/C disabled by default |
| Grid frequency | 26 | Hz | |
| Battery state of charge | 258 | % | |
| Battery voltage | 256 | V | |
| Battery current | 257 | A | Positive = discharge |
| Battery power | 294 | W | Negative = charging |
| Minimum / maximum cell temperature | 269 / 272 | °C | |
| Maximum charge / discharge current | 273 / 274 | A | |
| Battery capacity | 281 | kWh | |
| Battery state of health | 283 | % | |
| Battery charge energy | 288–289 | kWh | Total increasing |
| Battery discharge energy | 290–291 | kWh | Total increasing |
| Battery energy charged from grid | 292–293 | kWh | Total increasing |
| Remaining time | 295 | min | |
| Relay status | 260 | – | Enum: disconnected / discharge relay closed / charge relay closed / both closed |
| Minimum / maximum cell voltage | 263 / 266 | V | Disabled by default |
| Battery module count | 280 | – | Disabled by default, diagnostic |
| Battery status code | 259 | – | Disabled by default, diagnostic |
| Battery warning / fault bitmap | 284–285 / 286–287 | – | Disabled by default, diagnostic |
| PV power total | derived | W | PV1 power + PV2 power |
| PV energy total | 1086–1087 | kWh | Total increasing |
| PV1 voltage / current / power | 1053 / 1054 / 1055–1056 | V / A / W | |
| PV2 voltage / current / power | 1057 / 1058 / 1059–1060 | V / A / W | Disabled by default |
| Inverter power | 1036–1037 (int32) | W | |
| Inverter power L1 | 1030–1031 (int32) | W | Disabled by default |
| Inverter voltage L1 | 1024 | V | |
| Inverter current L1 | 1027 | A | |
| Inverter frequency | 1052 | Hz | |
| Inverter temperature | 1077 | °C | |
| Inverter work mode | 1088 | – | Enum: wait / online / UPS / bypass / fault / DC / self test / check / update master / update slave / update ARM |
| Backup power | 1050–1051 | W | |
| Backup power L1 | 1044–1045 | W | Disabled by default |
| Backup voltage / current L1 | 1038 / 1041 | V / A | Disabled by default |
| Inverter fault code 1 / 2 | 1082–1083 / 1084–1085 | – | Disabled by default, diagnostic |
| Inverter extended fault code 1 / 2 | 1099–1100 / 1101–1102 | – | Disabled by default, diagnostic |
| System fault bitmap | 1793–1794 | – | Disabled by default, diagnostic |
| House load power | derived | W | Inverter power + grid power |
| House load energy | derived | kWh | PV energy + grid consumption − grid feed-in |
| Dispatch duration | 2183–2184 | s | Remaining/set dispatch duration |

### Binary sensors

| Entity | Source | Notes |
| --- | --- | --- |
| Exporting to grid | grid power < 0 | |
| Importing from grid | grid power > 0 | Disabled by default |
| Battery charging | battery power < 0 | |
| Battery discharging | battery power > 0 | Disabled by default |
| System fault | fault bitmaps ≠ 0 | Problem class, fires on any system/battery/inverter fault |
| Inverter online | work mode = online | Connectivity class |

### Numbers (writable setpoints)

| Entity | Register(s) | Range | Notes |
| --- | --- | --- | --- |
| UPS reserve state of charge | 1810 + 2128 | 4–100 % | Written as 0.1 %/bit to both documented registers |
| Max feed to grid | 2048 | 0–100 % | 1 %/bit |

### Select

| Entity | Register | Options |
| --- | --- | --- |
| Dispatch mode | 2181 | Battery only charges from PV, State of charge control, Load following, Maximise output, Normal mode, Optimise consumption, Maximise consumption, ECO mode, PV power setting, No battery charge |

### Switches

| Entity | Register(s) | Behaviour |
| --- | --- | --- |
| Power dispatch | 2176 | Start (1) / stop (0) the configured dispatch mode |
| Battery charge block | 2181, 2183–2184, 2176 | On: writes mode 19 "No battery charge", the configured duration and starts the dispatch. Off: stops the dispatch. Mirrors the typical input_boolean + automation pattern in a single entity |

## Sign conventions

- **Grid power**: positive = importing from the grid, negative = feeding in
- **Battery power/current**: negative = charging, positive = discharging
- Energy totals use `state_class: total_increasing`, so they are directly usable in the Home Assistant **Energy dashboard**

## Troubleshooting

- **Connection fails during setup**: verify Modbus TCP is enabled on the inverter, the IP/port are correct and nothing else holds exclusive access to the connection.
- **Entities unavailable**: the last poll failed; check reachability of the inverter. Values recover automatically once communication works again.
- **Unexpected values**: make sure the slave ID matches the one configured in the inverter (`0x55`/85 by default).

## License

Apache License 2.0 — see [LICENSE](LICENSE).
