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
<to be done>
 
# Example code

