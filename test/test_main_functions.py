import unittest
import os


import pandas as pd


from src.main_functions import clean_CDP_year, create_CDP_clean_dataset


class TestCleanCDPYear(unittest.TestCase):
    def test_clean_CDP_year_create_empty(self):
        # Set up parameters
        path_clean_data = os.path.join("data", "test_data")
        path_clean_data = os.path.join("data", "test_data")
        year = 2014
        save_years = "xlsx"

        # Test creating a new cleaned dataset
        expected_columns = [
            "account_id",
            "account_name",
            "country",
            "activity",
            "sector",
            "industry",
            "isin",
            "ticker",
            "accounting_year",
            "boundary",
            "covered_countries",
            "CDP_CF1",
            "CDP_CF2_location",
            "CDP_CF2_market",
            "CDP_CF3",
            "CF3_relevance",
            "unique_id",
            "questionnaire_year",
        ]
        df_cleaned = clean_CDP_year(path_clean_data, path_clean_data, year, save_years)
        self.assertIsInstance(df_cleaned, pd.DataFrame)
        self.assertTrue(
            all(col in df_cleaned.columns for col in expected_columns)
        )  # Check for expected columns


class TestCreateCDPCleanDataset(unittest.TestCase):
    def test_create_CDP_clean_dataset(self):
        # Initialize variables or set up necessary data for testing
        years = [2015, 2022]
        path_clean_data = os.path.join("data", "test_data")
        save_years = False
        save_format = False
        expected_columns = [
            "account_id",
            "account_name",
            "country",
            "activity",
            "sector",
            "industry",
            "isin",
            "ticker",
            "accounting_year",
            "boundary",
            "covered_countries",
            "CDP_CF1",
            "CDP_CF2_location",
            "CDP_CF2_market",
            "CDP_CF3",
            "CF3_relevance",
            "unique_id",
            "questionnaire_year",
        ]

        # Apply the function
        df_cleaned = create_CDP_clean_dataset(
            years=years,
            path_clean_data=path_clean_data,
            save_years=save_years,
            save_format=save_format,
        )
        self.assertIsInstance(df_cleaned, pd.DataFrame)
        self.assertEqual(len(df_cleaned), 200)  # Compare with an expected length
        self.assertTrue(
            all(col in df_cleaned.columns for col in expected_columns)
        )  # Check for expected columns


if __name__ == "__main__":
    unittest.main()
