# The MIT License (MIT)
#
# Copyright (c) 2017 Dean Miller for Adafruit Industries
# Copyright (c) 2020 Christian Becker
# Copyright (c) 2026
#
# Micropython driver for the INA226 current/power monitor.

from micropython import const

__version__ = "0.2.0"
__repo__ = "https://github.com/elschopi/TI_INA226_micropython.git"

# Registers
_REG_CONFIG        = const(0x00)
_REG_SHUNTVOLTAGE  = const(0x01)
_REG_BUSVOLTAGE    = const(0x02)
_REG_POWER         = const(0x03)
_REG_CURRENT       = const(0x04)
_REG_CALIBRATION   = const(0x05)

# Config bits
_CONFIG_RESET      = const(0x8000)
_CONFIG_CONST_BITS = const(0x4000)  # must be 1 per datasheet

# Averaging (AVG[2:0] bits at 11:9)
_AVG_1     = const(0x0000)
_AVG_4     = const(0x0200)
_AVG_16    = const(0x0400)
_AVG_64    = const(0x0600)
_AVG_128   = const(0x0800)
_AVG_256   = const(0x0A00)
_AVG_512   = const(0x0C00)
_AVG_1024  = const(0x0E00)

# Bus voltage conversion time (VBUSCT[2:0] bits at 8:6)
_VBUSCT_140US  = const(0x0000)
_VBUSCT_204US  = const(0x0040)
_VBUSCT_332US  = const(0x0080)
_VBUSCT_588US  = const(0x00C0)
_VBUSCT_1100US = const(0x0100)
_VBUSCT_2116US = const(0x0140)
_VBUSCT_4156US = const(0x0180)
_VBUSCT_8244US = const(0x01C0)

# Shunt voltage conversion time (VSHCT[2:0] bits at 5:3)
_VSHCT_140US  = const(0x0000)
_VSHCT_204US  = const(0x0008)
_VSHCT_332US  = const(0x0010)
_VSHCT_588US  = const(0x0018)
_VSHCT_1100US = const(0x0020)
_VSHCT_2116US = const(0x0028)
_VSHCT_4156US = const(0x0030)
_VSHCT_8244US = const(0x0038)

# Operating mode (MODE[2:0] bits at 2:0)
_MODE_POWERDOWN              = const(0x0000)
_MODE_SHUNT_TRIGGERED        = const(0x0001)
_MODE_BUS_TRIGGERED          = const(0x0002)
_MODE_SHUNT_BUS_TRIGGERED    = const(0x0003)
_MODE_ADC_OFF                = const(0x0004)
_MODE_SHUNT_CONTINUOUS       = const(0x0005)
_MODE_BUS_CONTINUOUS         = const(0x0006)
_MODE_SHUNT_BUS_CONTINUOUS   = const(0x0007)

# LSBs per datasheet
_SHUNT_V_LSB_V = 0.0000025   # 2.5uV/bit
_BUS_V_LSB_V   = 0.00125     # 1.25mV/bit

# Calibration constant per datasheet
_CALIBRATION_FACTOR = 0.00512


def _to_signed_16(x):
    # Convert unsigned 16-bit to signed 16-bit
    if x & 0x8000:
        return x - 0x10000
    return x


class INA226:
    """
    INA226 MicroPython driver.

    Typical usage:
        ina = INA226(i2c, addr=0x40)
        ina.configure()  # optional, defaults are sensible
        ina.calibrate(r_shunt_ohms=0.1, max_expected_amps=3.6)
        vbus = ina.bus_voltage
        ishunt = ina.current
        p = ina.power
    """

    # Expose some "enum-like" values for users
    AVG_1, AVG_4, AVG_16, AVG_64, AVG_128, AVG_256, AVG_512, AVG_1024 = (
        _AVG_1, _AVG_4, _AVG_16, _AVG_64, _AVG_128, _AVG_256, _AVG_512, _AVG_1024
    )
    VBUSCT_140US, VBUSCT_204US, VBUSCT_332US, VBUSCT_588US, VBUSCT_1100US, VBUSCT_2116US, VBUSCT_4156US, VBUSCT_8244US = (
        _VBUSCT_140US, _VBUSCT_204US, _VBUSCT_332US, _VBUSCT_588US, _VBUSCT_1100US, _VBUSCT_2116US, _VBUSCT_4156US, _VBUSCT_8244US
    )
    VSHCT_140US, VSHCT_204US, VSHCT_332US, VSHCT_588US, VSHCT_1100US, VSHCT_2116US, VSHCT_4156US, VSHCT_8244US = (
        _VSHCT_140US, _VSHCT_204US, _VSHCT_332US, _VSHCT_588US, _VSHCT_1100US, _VSHCT_2116US, _VSHCT_4156US, _VSHCT_8244US
    )
    MODE_POWERDOWN, MODE_SHUNT_TRIGGERED, MODE_BUS_TRIGGERED, MODE_SHUNT_BUS_TRIGGERED, MODE_ADC_OFF, MODE_SHUNT_CONTINUOUS, MODE_BUS_CONTINUOUS, MODE_SHUNT_BUS_CONTINUOUS = (
        _MODE_POWERDOWN, _MODE_SHUNT_TRIGGERED, _MODE_BUS_TRIGGERED, _MODE_SHUNT_BUS_TRIGGERED, _MODE_ADC_OFF, _MODE_SHUNT_CONTINUOUS, _MODE_BUS_CONTINUOUS, _MODE_SHUNT_BUS_CONTINUOUS
    )

    def __init__(self, i2c, addr=0x40):
        self.i2c = i2c
        self.addr = addr
        self._buf = bytearray(2)

        # Scaling derived from calibration
        self._cal_value = 0
        self._current_lsb_a = None  # amps/bit
        self._power_lsb_w = None    # watts/bit

        # Keep last written config for quick reapply
        self._config = None

        # Reasonable defaults (similar intent to your README defaults)
        self.configure(
            avg=_AVG_512,
            vbusct=_VBUSCT_588US,
            vshct=_VSHCT_588US,
            mode=_MODE_SHUNT_BUS_CONTINUOUS,
        )

        # Default calibration equivalent to your original (0.1 ohm, ~3.6A max expected, rounded current_lsb)
        # You can remove this if you prefer forcing explicit calibrate()
        self.calibrate(r_shunt_ohms=0.1, max_expected_amps=3.6, current_lsb_a=0.0001)

    # ----------------------------
    # Low-level I2C register access
    # ----------------------------
    def _write_u16(self, reg, value):
        self._buf[0] = (value >> 8) & 0xFF
        self._buf[1] = value & 0xFF
        self.i2c.writeto_mem(self.addr, reg, self._buf)

    def _read_u16(self, reg):
        self.i2c.readfrom_mem_into(self.addr, reg, self._buf)
        return (self._buf[0] << 8) | self._buf[1]

    # ----------------------------
    # Configuration / calibration
    # ----------------------------
    def reset(self):
        """Soft-reset the chip via config register."""
        self._write_u16(_REG_CONFIG, _CONFIG_RESET)
        # After reset, calibration becomes 0; we'll reapply lazily on next current/power read.

    def configure(self, *, avg=_AVG_512, vbusct=_VBUSCT_588US, vshct=_VSHCT_588US, mode=_MODE_SHUNT_BUS_CONTINUOUS):
        """
        Configure conversion/averaging settings.

        Pass values using INA226.AVG_..., INA226.VBUSCT_..., INA226.VSHCT_..., INA226.MODE_...
        """
        config = _CONFIG_CONST_BITS | avg | vbusct | vshct | mode
        self._config = config
        self._write_u16(_REG_CONFIG, config)
        return config

    def calibrate(self, *, r_shunt_ohms, max_expected_amps=None, current_lsb_a=None, cal_value=None):
        """
        Set calibration and scaling factors.

        Preferred: provide r_shunt_ohms + max_expected_amps (optionally also current_lsb_a to choose a nice rounded LSB).
          - current_lsb_a default: max_expected_amps / 32768
          - power_lsb_w is always 25 * current_lsb_a for INA226

        Advanced: provide cal_value and current_lsb_a directly (and r_shunt_ohms is still required for sanity).
        """
        if r_shunt_ohms is None or r_shunt_ohms <= 0:
            raise ValueError("r_shunt_ohms must be > 0")

        # If user explicitly provides cal_value, we require current_lsb_a too (otherwise scaling is unknown)
        if cal_value is not None:
            if current_lsb_a is None or current_lsb_a <= 0:
                raise ValueError("When cal_value is provided, current_lsb_a must be provided and > 0")
            self._cal_value = int(cal_value) & 0xFFFF
            self._current_lsb_a = float(current_lsb_a)
            self._power_lsb_w = 25.0 * self._current_lsb_a
            self._write_u16(_REG_CALIBRATION, self._cal_value)
            return self._cal_value

        # Otherwise compute cal_value from r_shunt and current_lsb
        if current_lsb_a is None:
            if max_expected_amps is None or max_expected_amps <= 0:
                raise ValueError("Provide max_expected_amps (>0) or current_lsb_a (>0)")
            current_lsb_a = max_expected_amps / 32768.0
        else:
            if current_lsb_a <= 0:
                raise ValueError("current_lsb_a must be > 0")

        cal = _CALIBRATION_FACTOR / (r_shunt_ohms * current_lsb_a)
        cal_int = int(cal)

        # Datasheet: calibration register is 15-bit? Practically stored in 16-bit register.
        # Guardrails: avoid 0 which disables current/power calculations.
        if cal_int <= 0:
            cal_int = 1
        if cal_int > 0xFFFF:
            cal_int = 0xFFFF

        self._cal_value = cal_int
        self._current_lsb_a = float(current_lsb_a)
        self._power_lsb_w = 25.0 * self._current_lsb_a

        self._write_u16(_REG_CALIBRATION, self._cal_value)
        return self._cal_value

    def _ensure_calibration(self):
        """
        Ensure calibration register matches our expected value.
        Called before current/power reads to self-heal after brownouts/resets.
        """
        if not self._cal_value:
            # Not calibrated; user must call calibrate()
            raise RuntimeError("INA226 is not calibrated. Call calibrate(...) first.")

        # Only read+rewrite if needed (faster than always writing)
        if self._read_u16(_REG_CALIBRATION) != self._cal_value:
            self._write_u16(_REG_CALIBRATION, self._cal_value)

    # ----------------------------
    # Measurement properties
    # ----------------------------
    @property
    def shunt_voltage(self):
        """Shunt voltage in Volts (signed)."""
        raw = _to_signed_16(self._read_u16(_REG_SHUNTVOLTAGE))
        return raw * _SHUNT_V_LSB_V

    @property
    def bus_voltage(self):
        """Bus voltage in Volts (unsigned)."""
        raw = self._read_u16(_REG_BUSVOLTAGE)
        return raw * _BUS_V_LSB_V

    @property
    def current(self):
        """Current in Amps (signed). Requires calibration."""
        self._ensure_calibration()
        if self._current_lsb_a is None:
            raise RuntimeError("current_lsb not set; call calibrate(...)")

        raw = _to_signed_16(self._read_u16(_REG_CURRENT))
        return raw * self._current_lsb_a

    @property
    def power(self):
        """Power in Watts (signed). Requires calibration."""
        self._ensure_calibration()
        if self._power_lsb_w is None:
            raise RuntimeError("power_lsb not set; call calibrate(...)")

        raw = _to_signed_16(self._read_u16(_REG_POWER))
        return raw * self._power_lsb_w

    # Convenience helpers
    @property
    def current_mA(self):
        """Current in milliamps."""
        return self.current * 1000.0

    @property
    def power_mW(self):
        """Power in milliwatts."""
        return self.power * 1000.0

    def read_all(self):
        """
        Read bus V, shunt V, current, power (in that order).
        Note: this performs multiple I2C reads.
        """
        return (self.bus_voltage, self.shunt_voltage, self.current, self.power)
