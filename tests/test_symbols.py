import contextlib
import io
import unittest

from labplotlib import print_symbols, search, symbols


class SymbolTests(unittest.TestCase):
    def test_search_returns_matching_symbols(self):
        result = search("fraction_one")

        self.assertIn("fraction_one_half_1_2", result)
        self.assertNotIn("set_union", result)

    def test_symbol_mappings_are_read_only(self):
        with self.assertRaises(TypeError):
            symbols["new_symbol"] = "x"

    def test_search_is_case_insensitive(self):
        self.assertEqual(dict(search("DELTA")), dict(search("delta")))
        self.assertTrue(search("DELTA"))

    def test_print_symbols_handles_multichar_and_astral(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_symbols(search("degree_celsius"))
            print_symbols(search("set_universal"))

        output = buffer.getvalue()
        self.assertIn("\\u00b0 \\u0043", output)
        self.assertIn("\\U0001d54c", output)

    def test_renamed_symbols(self):
        self.assertIn("plus_minus", symbols)
        self.assertNotIn("+/-", symbols)
        self.assertEqual(symbols["approximately_equal_to"], "≈")


if __name__ == "__main__":
    unittest.main()
