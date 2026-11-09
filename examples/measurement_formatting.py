"""Demonstrate measurement formatting and display-only units."""

from labplotlib import Measurement


def main() -> None:
    pressure = Measurement.from_pm(2_000_000, 100_000)
    print("Automatic:", pressure)
    print("Raw:", pressure.to_string(format="raw"))
    print("Scientific:", pressure.to_string(format="scientific", decimals=1))
    print("Unrounded:", pressure.to_string(format="scientific", decimals=None))

    pressure.set_unit("Pa", "mega")
    print("Stored display unit:", pressure)
    print("Alternate prefix:", pressure.to_string(prefix="kilo"))
    print("Stored value in Pa:", pressure.value)

    doubled = pressure * 2
    print("Arithmetic result (no unit metadata):", doubled)
    doubled.set_unit("Pa", "mega")
    print("Arithmetic result with display unit:", doubled)


if __name__ == "__main__":
    main()
