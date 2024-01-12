import unittest
import pandas as pd
import numpy as np

from pandas.testing import assert_frame_equal, assert_series_equal

from src.get_year_functions import (
    str_to_accounting_year,
    keep_main_boundary,
    dict_to_relevance,
    preprocess_covered_countries,
    preprocess_accounting_years,
    attribute_CF3_to_last_year,
    common_final_cleaning,
)


class TestPreprocessCoveredCountries(unittest.TestCase):
    def test_preprocess_covered_countries(self):
        # Create a sample DataFrame with covered countries data
        data = {
            "account_id": [1, 1, 2, 2],
            "country_1": [None, "Canada", "Germany", "France"],
            "country_2": ["UK", None, None, None],
        }
        df = pd.DataFrame(data)

        # Test the function
        result = preprocess_covered_countries(df)

        # Perform assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.columns.tolist(), ["account_id", "covered_countries"])
        self.assertEqual(len(result), 2)
        data = {
            "account_id": [1, 2],
            "covered_countries": ['["UK","Canada"]', '["Germany","France"]'],
        }
        ground_truth = pd.DataFrame(data)
        assert_frame_equal(result, ground_truth)


class TestStrToAccountingYear(unittest.TestCase):
    def test_valid_dates(self):
        self.assertEqual(str_to_accounting_year(20090702), 2009)
        self.assertEqual(str_to_accounting_year(20100630), 2009)
        self.assertEqual(str_to_accounting_year(20100701), 2010)
        self.assertEqual(str_to_accounting_year(20230630), 2022)
        self.assertEqual(str_to_accounting_year(20230701), 2023)

    def test_boundary_dates(self):
        self.assertEqual(str_to_accounting_year(20090701), 2009)
        self.assertEqual(str_to_accounting_year(20240701), 2024)
        self.assertNotEqual(
            str_to_accounting_year(20090630), str_to_accounting_year(20090630)
        )
        self.assertNotEqual(
            str_to_accounting_year(20250701), str_to_accounting_year(20240702)
        )

    def test_invalid_dates(self):
        self.assertNotEqual(
            str_to_accounting_year(20091301), str_to_accounting_year(20091301)
        )  # Invalid month
        self.assertNotEqual(
            str_to_accounting_year(20220230), str_to_accounting_year(20220230)
        )  # Invalid day
        self.assertNotEqual(
            str_to_accounting_year(202), str_to_accounting_year(202)
        )  # Invalid format


class TestPreprocessAccountingYears(unittest.TestCase):
    def test_preprocess_accounting_years(self):
        # Create a sample DataFrame with accounting year data
        data = {
            "C0.2_C1_State the start and end date of the year for which you are reporting data. - Start date": [
                "2022-01-01",
                "2021-01-01",
                "Question not applicable",
                "2022-07-01",
                "2022-07-01",
            ],
            "C0.2_C2_State the start and end date of the year for which you are reporting data. - End date": [
                "2022-12-31",
                "2021-12-31",
                "2020-12-31",
                "2022-06-30",
                "2022-07-01",
            ],
        }
        df = pd.DataFrame(data)

        # Test the function
        result = preprocess_accounting_years(df)

        # Perform assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)
        self.assertEqual(len(result.columns), 5)
        ground_truth = pd.Series([2022, 2021, 2021, 2022], name="accounting_year")
        assert_series_equal(result.accounting_year, ground_truth)


class TestKeepMainBoundary(unittest.TestCase):
    def test_valid_boundaries(self):
        self.assertEqual(
            keep_main_boundary("Operational control"), "Operational control"
        )
        self.assertEqual(keep_main_boundary("Financial control"), "Financial control")
        self.assertEqual(keep_main_boundary("Equity share"), "Equity share")

    def test_invalid_boundaries(self):
        self.assertNotEqual(
            keep_main_boundary("Controle opérationnel"),
            keep_main_boundary("Controle opérationnel"),
        )  # Invalid format
        self.assertNotEqual(
            keep_main_boundary(12), keep_main_boundary(12)
        )  # Invalid type


class TestDictToRelevance(unittest.TestCase):
    def test_relevant_dict(self):
        dict_test = {
            "Not evaluated": 1,
            "Question not applicable": 1,
            "Relevant, calculated": 1,
            "Relevant, not yet calculated": 1,
            "Not relevant, calculated": 1,
        }
        self.assertEqual(dict_to_relevance(dict_test), 0.5)
        dict_test["Not evaluated"] = 0
        self.assertEqual(dict_to_relevance(dict_test), 2 / 3)
        dict_test["Relevant, not yet calculated"] = 0
        self.assertEqual(dict_to_relevance(dict_test), 1)
        dict_test["Not relevant, calculated"] = 0
        self.assertEqual(dict_to_relevance(dict_test), 1)
        dict_test["Relevant, calculated"] = 0
        self.assertEqual(dict_to_relevance(dict_test), 0)

    def test_not_relevant_dict(self):
        dict_test = {
            "Relevant": 1,
        }
        self.assertEqual(dict_to_relevance(dict_test), 0)  # Invalid key format


class TestAttributeCF3ToLastYear(unittest.TestCase):
    def test_attribute_CF3_to_last_year(self):
        # Create a sample DataFrame
        data = {
            "account_id": [1, 1, 2, 2, 2],
            "accounting_year": [2020, 2021, 2021, 2020, 2019],
            "CDP_CF3": [100, 200, 300, 400, 500],
            "CF3_relevance": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
        df = pd.DataFrame(data)

        # Test the function
        result = attribute_CF3_to_last_year(df)

        # Perform assertions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 5)
        self.assertEqual(len(result.columns), 4)
        data = {
            "account_id": [1, 1, 2, 2, 2],
            "accounting_year": [2020, 2021, 2021, 2020, 2019],
            "CDP_CF3": [np.nan, 200, 300, np.nan, np.nan],
            "CF3_relevance": [np.nan, 0.2, 0.3, np.nan, np.nan],
        }
        ground_truth = pd.DataFrame(data)
        assert_frame_equal(result, ground_truth)


class TestCommonFinalCleaning(unittest.TestCase):
    def setUp(self):
        # Sample input DataFrame
        data = {
            "Organization": ["Org1", "Org2"],
            "Account number": [1, 2],
            "Primary activity": ["Act1", "Act2"],
            "Country/Areas_x": ["USA", "CAN"],
            "Primary sector_x": ["Sect2", "Sect2"],
            "Primary industry_x": ["Ind1", "Ind2"],
            "ISINs": ["Org1", "Org2"],
            "Tickers": ["Org1", "Org2"],
            "accounting_year": [2022, 2021],
            "boundary": ["Operational control", np.nan],
            "covered_countries": np.nan,
            "CDP_CF1": [1, 10],
            "CDP_CF2_location": ["Question not applicable", 100],
            "CDP_CF2_market": [50, "Question not applicable"],
            "CDP_CF3": [10, 100],
            "CF3_relevance": [1, 0.5],
            "unique_id": ["1_2022", "2_2021"],
        }
        self.df = pd.DataFrame(data)

    def test_common_final_cleaning(self):
        # Apply function to test DataFrame
        result = common_final_cleaning(self.df)

        # Check if result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)

        # Check for expected columns after filtering and renaming
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
        ]
        self.assertCountEqual(result.columns.tolist(), expected_columns)

        # Check for NaN values in specific columns after cleaning
        self.assertFalse(
            result[["account_id", "accounting_year"]].isnull().values.any()
        )

        # Check data types
        self.assertEqual(result["accounting_year"].dtype, np.int64)

        # Check application of keep_main_boundary to 'boundary' column
        self.assertTrue(
            result["boundary"]
            .isin(["Operational control", "Financial control", "Equity share", np.nan])
            .all()
        )

        # Check values replaced from 'Question not applicable' to NaN and converted to float
        self.assertTrue(result["CDP_CF2_location"].isna().any())
        self.assertTrue(result["CDP_CF2_market"].isna().any())
        self.assertEqual(result["CDP_CF2_location"].dtype, float)
        self.assertEqual(result["CDP_CF2_market"].dtype, float)

        # Check index reset
        self.assertTrue(result.index.equals(pd.RangeIndex(start=0, stop=len(result))))


if __name__ == "__main__":
    unittest.main()
