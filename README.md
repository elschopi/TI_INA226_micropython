# TI_INA226_micropython

MicroPython driver for the TI INA226 current / power monitor IC.

Datasheet and IC info: https://www.ti.com/product/INA226

This library was originally derived from https://github.com/robert-hh/INA219 and adapted for INA226.

## Key points (INA226 specifics)

- **Shunt voltage LSB is 2.5 µV/bit** (signed register).
- **Bus voltage LSB is 1.25 mV/bit** (unsigned register).
- To read **current** and **power**, you must set the **calibration register**. Without calibration, the chip’s CURRENT/POWER registers are not valid.

## Driver overview

The driver provides:

- `configure(...)` for conversion timing / averaging / operating mode
- `calibrate(...)` for calibration register + current/power scaling
- Properties:
  - `bus_voltage` (V)
  - `shunt_voltage` (V)
  - `current` (A) and `current_mA` (mA)
  - `power` (W) and `power_mW` (mW)

## Installation / files

- `ina226.py` — the driver
- `ina_calc_conf.py` — interactive helper to build a config register value and print a ready-to-paste `configure()` call

## Configuration register

INA226 configuration register layout (high-level):

```
CONFIG = CONST_BITS + AVG + VBUSCT + VSHCT + MODE
```

Where:
- `AVG` controls averaging (1..1024 samples)
- `VBUSCT` is bus voltage conversion time
- `VSHCT` is shunt voltage conversion time
- `MODE` selects triggered/continuous shunt/bus conversions

The driver exposes constants like:
- `INA226.AVG_512`
- `INA226.VBUSCT_588US`
- `INA226.VSHCT_588US`
- `INA226.MODE_SHUNT_BUS_CONTINUOUS`

## Calibration (auto-calculation)

The driver can compute calibration values automatically.

You must provide:
- `r_shunt_ohms` (your shunt resistor value in ohms)
- and either:
  - `max_expected_amps` (recommended)
  - or `current_lsb_a` (advanced; choose a “nice” LSB)

### How it works (summary)

- Choose `current_lsb_a` (amps/bit). Default:
  - `current_lsb_a = max_expected_amps / 32768`
- Compute calibration register:
  - `cal_value = 0.00512 / (r_shunt_ohms * current_lsb_a)`
- Power LSB is fixed relationship:
  - `power_lsb_w = 25 * current_lsb_a`

## Example (ESP / generic MicroPython)

```python
import ina226
from machine import Pin, I2C

# Adjust pins for your board
i2c = I2C(scl=Pin(2), sda=Pin(0))

ina = ina226.INA226(i2c, addr=0x40)

# Optional: configure conversion behavior (defaults are already reasonable)
ina.configure(
    avg=ina226.INA226.AVG_512,
    vbusct=ina226.INA226.VBUSCT_588US,
    vshct=ina226.INA226.VSHCT_588US,
    mode=ina226.INA226.MODE_SHUNT_BUS_CONTINUOUS,
)

# Auto-calibrate (recommended)
ina.calibrate(r_shunt_ohms=0.1, max_expected_amps=3.6)

print("Bus voltage:", ina.bus_voltage, "V")
print("Shunt voltage:", ina.shunt_voltage, "V")
print("Current:", ina.current, "A")
print("Power:", ina.power, "W")

# Or convenience in mA / mW
print("Current:", ina.current_mA, "mA")
print("Power:", ina.power_mW, "mW")
```

### Using a “nice” rounded current LSB (optional)

If you want a specific current resolution (example: 100 µA/bit):

```python
ina.calibrate(r_shunt_ohms=0.1, max_expected_amps=3.6, current_lsb_a=0.0001)
```

## Troubleshooting

- If `current` / `power` raises “not calibrated”: call `calibrate(...)`.
- After brown-outs / resets the INA226 may clear the calibration register; the driver automatically re-applies it when reading current/power.
