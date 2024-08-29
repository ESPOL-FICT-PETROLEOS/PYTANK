import numpy as np
import pytest
import pandas as pd
from pytank.functions.utilities import normalize_date_freq
import unittest


class TestNormalizeDateFreq(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame
        self.data = {
            "A": [1, 2, 3, 4, 5],
            "B": [10, 20, 30, 40, 50],
            "C": [100, 200, 300, 400, 500],
        }
        self.df = pd.DataFrame(
            self.data, index=pd.date_range("2022-01-01", periods=5, freq="D")
        )

    def test_normalize_with_valid_freq(self):
        # Test with a valid frequency
        normalized_df = normalize_date_freq(self.df, freq="2D")
        self.assertEqual(len(normalized_df), 3)
        self.assertEqual(normalized_df.index[0], pd.Timestamp("2022-01-01"))
        self.assertEqual(normalized_df.index[-1], pd.Timestamp("2022-01-05"))

    def test_normalize_with_start_end_date(self):
        # Test with specific start and end dates
        normalized_df = normalize_date_freq(
            self.df, freq="2D", start_date="2022-01-02", end_date="2022-01-04"
        )
        self.assertEqual(len(normalized_df), 2)
        self.assertEqual(normalized_df.index[0], pd.Timestamp("2022-01-02"))
        self.assertEqual(normalized_df.index[-1], pd.Timestamp("2022-01-04"))

    def test_normalize_with_invalid_input(self):
        # Try invalid input (not DataFrame)
        with self.assertRaises(TypeError):
            normalize_date_freq([1, 2, 3], freq="2D")


if __name__ == "__main__":
    unittest.main()
