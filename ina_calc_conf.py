#!/usr/bin/env python3
"""INA226 Config register calculator (interactive helper)

- Helps compute the INA226 CONFIG register from menu selections.
- Prints the config hex value and a ready-to-paste MicroPython configure() call.
- Optionally prints a recommended calibrate() call.

This script runs on normal Python 3 (not MicroPython).
"""

CONST_BITS = 0x4000

AVG_OPTIONS = [
    ("1",    0x0000),
    ("4",    0x0200),
    ("16",   0x0400),
    ("64",   0x0600),
    ("128",  0x0800),
    ("256",  0x0A00),
    ("512",  0x0C00),
    ("1024", 0x0E00),
]

VBUSCT_OPTIONS = [
    ("140",  0x0000),
    ("204",  0x0040),
    ("332",  0x0080),
    ("588",  0x00C0),
    ("1100", 0x0100),
    ("2116", 0x0140),
    ("4156", 0x0180),
    ("8244", 0x01C0),
]

VSHCT_OPTIONS = [
    ("140",  0x0000),
    ("204",  0x0008),
    ("332",  0x0010),
    ("588",  0x0018),
    ("1100", 0x0020),
    ("2116", 0x0028),
    ("4156", 0x0030),
    ("8244", 0x0038),
]

MODE_OPTIONS = [
    ("POWERDOWN",      0x0000),
    ("SHUNT_TRIG",     0x0001),
    ("BUS_TRIG",       0x0002),
    ("SHUNT_BUS_TRIG", 0x0003),
    ("ADC_OFF",        0x0004),
    ("SHUNT_CONT",     0x0005),
    ("BUS_CONT",       0x0006),
    ("SHUNT_BUS_CONT", 0x0007),
]


def print_options(title, options):
    print("\n" + title)
    for k, v in options:
        print(f"  {k:>12} : 0x{v:04X}")


def choose_value(prompt, options):
    keys = {k: v for (k, v) in options}
    while True:
        raw = input(prompt).strip()
        if raw in keys:
            return keys[raw]
        print("Invalid input. Please choose one of:", ", ".join(keys.keys()))


def ask_float(prompt):
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return float(raw)
        except ValueError:
            print("Please enter a valid number or press Enter to skip.")


def _avg_name(avg_value):
    mapping = {
        0x0000: "1",
        0x0200: "4",
        0x0400: "16",
        0x0600: "64",
        0x0800: "128",
        0x0A00: "256",
        0x0C00: "512",
        0x0E00: "1024",
    }
    return mapping.get(avg_value, str(avg_value))


def _ct_name(ct_value):
    mapping = {
        0x0000: "140",
        0x0040: "204",
        0x0080: "332",
        0x00C0: "588",
        0x0100: "1100",
        0x0140: "2116",
        0x0180: "4156",
        0x01C0: "8244",
        0x0008: "204",
        0x0010: "332",
        0x0018: "588",
        0x0020: "1100",
        0x0028: "2116",
        0x0030: "4156",
        0x0038: "8244",
    }
    return mapping.get(ct_value, str(ct_value))


def _mode_name(mode_value):
    mapping = {
        0x0000: "POWERDOWN",
        0x0001: "SHUNT_TRIGGERED",
        0x0002: "BUS_TRIGGERED",
        0x0003: "SHUNT_BUS_TRIGGERED",
        0x0004: "ADC_OFF",
        0x0005: "SHUNT_CONTINUOUS",
        0x0006: "BUS_CONTINUOUS",
        0x0007: "SHUNT_BUS_CONTINUOUS",
    }
    return mapping.get(mode_value, str(mode_value))


def main():
    print("INA226 CONFIG register helper\n")

    print_options("Averaging samples (AVG)", AVG_OPTIONS)
    avg = choose_value("Select AVG (e.g. 512): ", AVG_OPTIONS)

    print_options("Bus voltage conversion time in µs (VBUSCT)", VBUSCT_OPTIONS)
    vbusct = choose_value("Select VBUSCT (e.g. 588): ", VBUSCT_OPTIONS)

    print_options("Shunt voltage conversion time in µs (VSHCT)", VSHCT_OPTIONS)
    vshct = choose_value("Select VSHCT (e.g. 588): ", VSHCT_OPTIONS)

    print_options("Operating mode (MODE)", MODE_OPTIONS)
    mode = choose_value("Select MODE (e.g. SHUNT_BUS_CONT): ", MODE_OPTIONS)

    config = CONST_BITS + avg + vbusct + vshct + mode

    print("\nResult")
    print("  CONFIG (hex):", hex(config))
    print("  CONFIG (bin):", f"{config:016b}")

    print("\nSuggested MicroPython code (ina226.py driver):")
    print("ina.configure(")
    print(f"    avg=ina226.INA226.AVG_{_avg_name(avg)},")
    print(f"    vbusct=ina226.INA226.VBUSCT_{_ct_name(vbusct)}US,")
    print(f"    vshct=ina226.INA226.VSHCT_{_ct_name(vshct)}US,")
    print(f"    mode=ina226.INA226.MODE_{_mode_name(mode)},")
    print(")")

    rshunt = ask_float("\nOptional: enter r_shunt_ohms (e.g. 0.1) or Enter to skip: ")
    if rshunt is not None:
        max_i = ask_float("Optional: enter max_expected_amps (e.g. 3.6) or Enter to skip: ")
        current_lsb = ask_float("Optional: enter current_lsb_a (e.g. 0.0001) or Enter to skip: ")

        if max_i is None and current_lsb is None:
            print("\nCalibration skipped (need max_expected_amps or current_lsb_a).")
        else:
            print("\nSuggested calibration call:")
            if current_lsb is None:
                print(f"ina.calibrate(r_shunt_ohms={rshunt}, max_expected_amps={max_i})")
            else:
                if max_i is None:
                    print(f"ina.calibrate(r_shunt_ohms={rshunt}, current_lsb_a={current_lsb})")
                else:
                    print(f"ina.calibrate(r_shunt_ohms={rshunt}, max_expected_amps={max_i}, current_lsb_a={current_lsb})")

    print("\nDone.")


if __name__ == "__main__":
    main()
