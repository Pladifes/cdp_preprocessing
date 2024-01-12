import pandas as pd
import unittest

from pandas.testing import assert_frame_equal
from src.utils import handle_duplicates, missing_value_imputation, clean_country_names


class TestHandleDuplicates(unittest.TestCase):
    def test_handle_duplicates(self):
        # Create a sample DataFrame with duplicated records
        data = {
            "unique_id": [
                "company1_2019",
                "company2_2019",
                "company1_2019",
                "company1_2020",
            ],
            "questionnaire_year": [
                2020,
                2020,
                2021,
                2021,
            ],
        }
        df = pd.DataFrame(data)

        # Test the function
        result = handle_duplicates(df)

        # Perform assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)  # Assuming duplicates are removed correctly


class TestMissingValueImputation(unittest.TestCase):
    def test_missing_value_imputation(self):
        # Create a sample DataFrame with missing values
        data = {
            "account_id": [1, 1, 2, 2],
            "isin": [None, "ABC", "XYZ", None],
            "ticker": ["PQR", None, "DEF", "DEF"],
            "covered_countries": ["USA", "USA", None, "CAN"],
            "activity": ["A", "A", None, "C"],
            "sector": [None, "X", "Y", None],
            "industry": [None, None, "Z", "Z"],
        }
        df = pd.DataFrame(data)

        # Test the function
        result = missing_value_imputation(df)

        # Perform assertions
        self.assertIsInstance(result, pd.DataFrame)
        data = {
            "account_id": [1, 1, 2, 2],
            "isin": ["ABC", "ABC", "XYZ", "XYZ"],
            "ticker": ["PQR", "PQR", "DEF", "DEF"],
            "covered_countries": ["USA", "USA", "CAN", "CAN"],
            "activity": ["A", "A", "C", "C"],
            "sector": ["X", "X", "Y", "Y"],
            "industry": [None, None, "Z", "Z"],
        }
        ground_truth = pd.DataFrame(data)
        assert_frame_equal(result, ground_truth)


class TestCleanCountryNames(unittest.TestCase):
    def test_clean_country_names(self):
        # Create a sample DataFrame with country names
        data = {
            "country": [
                "USA",
                "United Kingdom of Great Britain and Northern Ireland",
                "Canada",
                "Germany",
            ],
        }
        df = pd.DataFrame(data)

        # Test the function
        result = clean_country_names(df)

        # Perform assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result["country"].iloc[0], "United States of America")
        self.assertEqual(result["country"].iloc[1], "United Kingdom")


if __name__ == "__main__":
    unittest.main()
