from types import MappingProxyType
from typing import Mapping

symbols = MappingProxyType(
    {
        "set_empty": "∅",
        "set_union": "∪",
        "set_intersection": "∩",
        "set_is_element_of": "∈",
        "set_is_not_element_of": "∉",
        "set_is_subset_of": "⊆",
        "set_is_proper_subset_of": "⊂",
        "set_is_not_subset_of": "⊄",
        "set_is_superset_of": "⊇",
        "set_is_proper_superset_of": "⊃",
        "set_is_not_superset_of": "⊅",
        "set_universal": "𝕌",
        "set_minus": "∖",
        "set_cartesian_product": "×",
        "set_difference": "\\",
        "delta": "Δ",
        "set_cardinality": "|",
        "set_complement": "'",
        "set_power_set": "ℙ",
        "set_contains_as_member": "∋",
        "set_does_not_contain_as_member": "∌",
        "complex_numbers": "ℂ",
        "real_numbers": "ℝ",
        "rational_numbers": "ℚ",
        "integers": "ℤ",
        "natural_numbers": "ℕ",
        "superscript_i": "ⁱ",
        "superscript_n": "ⁿ",
        "superscript_plus_sign": "⁺",
        "superscript_minus": "⁻",
        "superscript_zero_0": "⁰",
        "superscript_one_1": "¹",
        "squared": "²",
        "superscript_three_3": "³",
        "superscript_four_4": "⁴",
        "superscript_five_5": "⁵",
        "superscript_six_6": "⁶",
        "superscript_seven_7": "⁷",
        "superscript_eight_8": "⁸",
        "superscript_nine_9": "⁹",
        "subscript_zero_0": "₀",
        "subscript_one_1": "₁",
        "subscript_two_2": "₂",
        "subscript_three_3": "₃",
        "subscript_four_4": "₄",
        "subscript_five_5": "₅",
        "subscript_six_6": "₆",
        "subscript_seven_7": "₇",
        "subscript_eight_8": "₈",
        "subscript_nine_9": "₉",
        "fraction_one_half_1_2": "½",
        "fraction_zero_thirds_0_3": "↉",
        "fraction_one_third_1_3": "⅓",
        "fraction_two_thirds_2_3": "⅔",
        "fraction_one_quarter_1_4": "¼",
        "fraction_three_quarters_3_4": "¾",
        "fraction_one_fifth_1_5": "⅕",
        "fraction_two_fifths_2_5": "⅖",
        "fraction_three_fifths_3_5": "⅗",
        "fraction_four_fifths_4_5": "⅘",
        "fraction_one_sixth_1_6": "⅙",
        "fraction_five_sixths_5_6": "⅚",
        "fraction_one_seventh_1_7": "⅐",
        "fraction_one_eighth_1_8": "⅛",
        "fraction_three_eighths_3_8": "⅜",
        "fraction_five_eighths_5_8": "⅝",
        "fraction_seven_eighths_7_8": "⅞",
        "fraction_one_ninth_1_9": "⅑",
        "fraction_one_tenth_1_10": "⅒",
        "degree": "°",
        "degree_celsius": "°C",
        "degree_fahrenheit": "°F",
        "diameter": "⌀",
        "multiplication": "×",
        "division": "÷",
        "left_floor": "⌊",
        "right_floor": "⌋",
        "left_ceiling": "⌈",
        "right_ceiling": "⌉",
        "product": "∏",
        "coproduct": "∐",
        "summation": "∑",
        "summation_top": "⎲",
        "summation_bottom": "⎳",
        "partial_differential": "∂",
        "integral": "∫",
        "top_half_integral": "⌠",
        "bottom_half_integral": "⌡",
        "not_sign": "¬",
        "plus_minus": "±",
        "square_root": "√",
        "cube_root": "∛",
        "fourth_root": "∜",
        "proportional_to": "∝",
        "infinity": "∞",
        "right_angle": "∟",
        "angle": "∠",
        "therefore": "∴",
        "approximately_equal_to": "≈",
        "congruent_to": "≅",
        "not_equal_to": "≠",
        "less_than_or_equal_to": "≤",
        "greater_than_or_equal_to": "≥",
        "right_angle_with_arc": "⊾",
        "right_triangle": "⊿",
        "dot_operator": "⋅",
        "sigma": "σ",
    }
)


def search(namelike: str) -> Mapping[str, str]:
    """
    Return a read-only mapping of the symbols whose names contain
    ``namelike``. The match is case-insensitive.
    """

    needle = namelike.lower()
    filtered = {k: v for k, v in symbols.items() if needle in k.lower()}

    return MappingProxyType(filtered)


def _hex_escape(char: str) -> str:
    code = ord(char)
    return f"\\u{code:04x}" if code <= 0xFFFF else f"\\U{code:08x}"


def print_symbols(symbols_to_print: Mapping[str, str] = symbols) -> None:
    """
    Print the symbols in ``symbols_to_print`` (all symbols by default)
    with their decimal and hexadecimal code points.
    """

    for name, value in symbols_to_print.items():
        decimal = " ".join(str(ord(c)) for c in value)
        hexadecimal = " ".join(_hex_escape(c) for c in value)
        print(f"{name:<32} {value}   decimal: {decimal:<8}   hexadecimal: {hexadecimal}")