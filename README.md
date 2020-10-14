# TI_INA226_micropython

This library provides support for the TI INA226 power measurement IC with micropython firmware.
Datasheet and other information on the IC: https://www.ti.com/product/INA226
#  
This library is derived from https://github.com/robert-hh/INA219 </br>
with the friendly support of the community at https://forum.micropython.org/
## Motivation
I needed a micropython library for the INA226 devices for a small power meter project I was working on. I did find libraries for the 
Raspberry Pi, but none for micropython. Thus, I had to modify an existing library for the INA219 devices.

# Basics

To use the device, it has to be configured at startup. In it's default configuration, the calibration register is not set and 
thus the current and power cannot be directly read out.</br>
By default, this library configures the device to a maximum current of 3.6 A and 36V bus voltage. Resistance of the shunt is assumed as 0.1 Ohm.

# Calculations

The following values need to be calculated in order to set the configuration and calibration register values:
- calibration register value
- power LSB value
- current LSB value
- configuration register value
Configuration register value is derived from the values of the corresponding bits.

Default configuration register is as follows:
|BitNr 	|	D15	|	D14	|	D13	|	D12	|	D11	|	D10	|	D09	|	D08	|	D07	|	D06	|	D05	|	D04	|	D03	|	D02	|	D01	|	D00	|
|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|---	|
|Name  	|RST	|N/A	|N/A	|N/A	|AVG2	|AVG1	|AVG0	|VBUSCT2|VBUSCT1|VBUSCT0|VSHCT2	|VSHCT1	|VSHCT0	|MODE3	|MODE2	|MODE1	|
|Value 	|	0	|	1	|	0	|	0	|	0	|	0	|	0	|	1	|	0	|	0	|	1	|	0	|	0	|	1	|	1	|	1	|

Default configuration according to the datasheet:
- Averaging mode: 1 sample
- Bus voltage conversion time: 1.1ms
- Shunt voltage conversion time: 1.1ms
- Operating mode: Shunt and Bus voltage, continuous

Possible values for the configuration registers can be found in the library.

## Calculating the current_LSB
As example, a maximum expected current of 3.6A is assumed.

current_LSB = max_expected_I / (2^15)</br>
current_LSB = 3.6 A / (2^15)</br>
current_LSB = 0.0001098632813 = 0.00011 = 0.0001 -> 100uA/bit</br>

## Calculating the calibration register

Cal_value = 0.00512 / (current_LSB * Rshunt)</br>
Cal_value = 0.00512 / (0.0001 * 0.1)</br>
Cal_value = 512</br>

## Calculating the power_LSB

power_LSB = 25 * current_LSB</br>
power_LSB = 25 * 0.0001 = 0.0025 -> 2.5mW/bit</br>

# Usage information
In order to be able to set calibration and configuration to custom values, some work needs to be done by the user</br>
In the library, a method "set_calibration_custom" exists, which expects the calibration register value and the </br>
configuration register value as arguments. If no arguments are given, it uses default values.</br>
For easier calculation, a Google spreadsheet is available at [this Google spreadsheet](https://docs.google.com/spreadsheets/d/1k0MbBsduRgoQ8huFrBwaHQnYhl97LjkpEw-sIXykTEg/edit?usp=sharing "INA226 Google Spreadsheet")
With ina_calc_config.py I've provided a crude, menu guided configuration calculator for Python3. It's a bit rough around the edges but works.

## Default values
`cal_value = 512`</br>
`current_lsb = 0.0001`</br>
`power_lsb = 0.0025`</br>
`Rshunt = 0.1`</br>
`Averaging mode = 512 samples`</br>
`Bus voltage conversion time = 588us`</br>
`Shunt voltage conversion time = 588us`</br>
`Operating mode = Shunt and Bus Voltage, continuous`</br>

# Example code
This code was written to test (i.e. just see if it works without errors) the library on an ESP01S module with 1MB flash

```python
import ina226
from time import sleep
from machine import Pin, I2C
# i2c
i2c = I2C(scl=Pin(2), sda=Pin(0))
# ina226
ina = ina226.INA226(i2c, 0x40)
# default configuration and calibration value
ina.set_calibration()
print(ina.bus_voltage)
print(ina.shunt_voltage)
print(ina.current)
print(ina.power)
```
