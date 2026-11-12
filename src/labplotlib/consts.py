"""Scientific constants in SI units (CODATA 2018; SI-defining values are exact).

Usage: ``from labplotlib import consts; consts.kb``
"""
if __package__:
    from .symbols import symbols
else:
    from symbols import symbols

SQ = symbols["squared"]


class Constant(float):
    """A float carrying a name, unit and reference.

    Behaves as a plain number, so it multiplies directly into a Measurement.
    """

    name: str
    unit: str
    ref: str

    def __new__(cls, name: str, value: float, unit: str, ref: str) -> "Constant":
        obj = super().__new__(cls, value)
        obj.name = name
        obj.unit = unit
        obj.ref = ref
        return obj

    @property
    def value(self) -> float:
        return float(self)

    def __repr__(self) -> str:
        return f"Constant({self.name}={float(self)!r} {self.unit}, ref='{self.ref}')"

# Exact (SI 2019 defining constants)
pi = Constant("pi", 3.141_592_653_589_793, "dimensionless", "SI 2019")  # pi [dimensionless]
c = Constant("c", 299_792_458.0, "m/s", "SI 2019")  # speed of light in vacuum [m/s]
h = Constant("h", 6.626_070_15e-34, "J s", "SI 2019")  # Planck constant [J s]
hbar = Constant("hbar", h / (2 * pi), "J s", "SI 2019")  # reduced Planck constant [J s]
e = Constant("e", 1.602_176_634e-19, "C", "SI 2019")  # elementary charge [C]
kb = Constant("kb", 1.380_649e-23, "J/K", "SI 2019")  # Boltzmann constant [J/K]
Na = Constant("Na", 6.022_140_76e23, "1/mol", "SI 2019")  # Avogadro constant [1/mol]
R = Constant("R", kb * Na, "J/(mol K)", "SI 2019")  # molar gas constant [J/(mol K)]
F = Constant("F", e * Na, "C/mol", "SI 2019")  # Faraday constant [C/mol]
sigma = Constant(
    "sigma",
    2 * pi**5 * kb**4 / (15 * h**3 * c**2),
    "W/(m^2 K^4)",
    "SI 2019",
)  # Stefan-Boltzmann constant [W/(m^2 K^4)]

# Measured (CODATA 2018)
g = Constant("g", 9.80665, f"m/s{SQ}", "CODATA 2018")  # standard gravity [m/s^2] (exact by definition)
G = Constant("G", 6.674_30e-11, f"m^3/(kg s{SQ})", "CODATA 2018")  # gravitational constant [m^3/(kg s^2)]
eps0 = Constant("eps0", 8.854_187_8128e-12, "F/m", "CODATA 2018")  # vacuum permittivity [F/m]
mu0 = Constant("mu0", 1.256_637_062_12e-6, f"N/A{SQ}", "CODATA 2018")  # vacuum permeability [N/A^2]
me = Constant("me", 9.109_383_7015e-31, "kg", "CODATA 2018")  # electron mass [kg]
mp = Constant("mp", 1.672_621_923_69e-27, "kg", "CODATA 2018")  # proton mass [kg]
mn = Constant("mn", 1.674_927_498_04e-27, "kg", "CODATA 2018")  # neutron mass [kg]
amu = Constant("amu", 1.660_539_066_60e-27, "kg", "CODATA 2018")  # atomic mass unit [kg]
alpha = Constant("alpha", 7.297_352_5693e-3, "dimensionless", "CODATA 2018")  # fine-structure constant [dimensionless]
rydberg = Constant("rydberg", 10_973_731.568_160, "1/m", "CODATA 2018")  # Rydberg constant [1/m]
bohr_radius = Constant("bohr_radius", 5.291_772_109_03e-11, "m", "CODATA 2018")  # Bohr radius [m]
muB = Constant("muB", 9.274_010_0783e-24, "J/T", "CODATA 2018")  # Bohr magneton [J/T]

# Conversions
ev = Constant("ev", float(e), "J", "SI 2019")  # electronvolt [J]
atm = Constant("atm", 101_325.0, "Pa", "CODATA 2018")  # standard atmosphere [Pa]
zero_celsius = Constant("zero_celsius", 273.15, "K", "CODATA 2018")  # 0 degC [K]

__all__ = [
    "alpha",
    "amu",
    "atm",
    "bohr_radius",
    "c",
    "e",
    "eps0",
    "ev",
    "F",
    "g",
    "G",
    "h",
    "hbar",
    "kb",
    "me",
    "mn",
    "mp",
    "mu0",
    "muB",
    "Na",
    "pi",
    "R",
    "rydberg",
    "sigma",
    "zero_celsius",
]

if __name__ == "__main__":
    for const in __all__:
        print(f"{const} = {globals()[const]}")