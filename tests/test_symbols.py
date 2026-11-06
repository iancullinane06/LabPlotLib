import unittest

from labplotlib import search, symbols


class SymbolTests(unittest.TestCase):
    def test_search_returns_matching_symbols(self):
        result = search("fraction_one")

        self.assertIn("fraction_one_half_1_2", result)
        self.assertNotIn("set_union", result)

    def test_symbol_mappings_are_read_only(self):
        with self.assertRaises(TypeError):
            symbols["new_symbol"] = "x"


if __name__ == "__main__":
    unittest.main()
