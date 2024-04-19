import pandas as pd
import numpy as np


from src.get_year import GetGivenYear
from src.get_year_functions import (
    load_useful_sheets,
    preprocess_covered_countries,
    common_final_cleaning,
    dict_to_relevance,
)


class Get2016(GetGivenYear):
    """
    Creates the clean datset for year 2016.

    This class is based on abstract class GetGivenYear.
    It uses generic functions from get_year_functions,
    as well as year specific methods/operations to format the data.
    The get_year_dataset method can be used to get the clean dataset."""

    def get_useful_sheets(self, path_raw_data):
        year = 2016
        return load_useful_sheets(year, path_raw_data)

    def get_covered_countries(self, df_countries):
        return preprocess_covered_countries(df_countries)

    def get_scopes_3(self, df_CF3):
        df_CF3_filtered = df_CF3[
            df_CF3["account_name"].map(df_CF3["account_name"].value_counts()) == 17
        ]
        emission_column = "CC14.1 C3 - Please account for your organization’s Scope 3 emissions, disclosing and explaining any exclusions - metric tonnes CO2e"
        df_CF3_calc = (
            df_CF3_filtered.groupby(["account_id", "accounting_year"])[emission_column]
            .sum()
            .to_frame("CDP_CF3")
        )

        evaluation_column = "CC14.1 C2 - Please account for your organization’s Scope 3 emissions, disclosing and explaining any exclusions - Evaluation status"
        evaluation_counts = df_CF3_filtered.groupby(["account_id", "accounting_year"])[
            evaluation_column
        ].value_counts()
        evaluation_counts_pivot = evaluation_counts.unstack().fillna(0)

        df_CF3_calc["CF3_relevance"] = evaluation_counts_pivot.apply(
            lambda row: dict_to_relevance(row.to_dict()), axis=1
        )
        return df_CF3_calc.reset_index()

    def preprocess_CF1(self, df_CF1):
        df_CF1 = df_CF1.rename(
            columns={
                "incorporated_country": "country",
                "CC8.1 - Please select the boundary you are using for your Scope 1 and 2 greenhouse gas inventory": "boundary",
                "CC8.2 - Please provide your gross global Scope 1 emissions figures in metric tonnes CO2e": "CDP_CF1",
            }
        )
        df_CF1 = df_CF1[
            [
                "account_id",
                "account_name",
                "country",
                "ticker",
                "isin",
                "accounting_year",
                "boundary",
                "CDP_CF1",
            ]
        ]
        return df_CF1

    def preprocess_CF2(self, df_CF2):
        df_CF2 = df_CF2.rename(
            columns={
                "CC8.3a C1 - Please provide your gross global Scope 2 emissions figures in metric tonnes CO2e\xa0 - Scope 2, location-based?": "CDP_CF2_location",
                "CC8.3a C2 - Please provide your gross global Scope 2 emissions figures in metric tonnes CO2e\xa0 - Scope 2, market-based (if applicable)?": "CDP_CF2_market",
            }
        )
        df_CF2 = df_CF2[
            ["account_id", "accounting_year", "CDP_CF2_location", "CDP_CF2_market"]
        ]
        return df_CF2

    def get_year_dataset(self, path_raw_data):
        (df_countries, df_CF1, df_CF2, df_CF3) = self.get_useful_sheets(path_raw_data)
        df_covered_countries = self.get_covered_countries(df_countries)
        df_CF3_calc = self.get_scopes_3(df_CF3)
        df_clean = self.preprocess_CF1(df_CF1)
        df_CF2 = self.preprocess_CF2(df_CF2)

        # Merging part
        df_clean = df_clean.merge(
            df_covered_countries[["account_id", "covered_countries"]],
            on="account_id",
            how="left",
        )
        df_clean = df_clean.merge(df_CF2, on=["account_id", "accounting_year"])
        df_clean = df_clean.merge(
            df_CF3_calc,
            on=["account_id", "accounting_year"],
            how="left",
        )

        # Year specific treatments
        df_clean["activity"] = np.nan
        df_clean["sector"] = np.nan
        df_clean["industry"] = np.nan

        df_clean = df_clean[
            ~((df_clean.account_id == 6532) & (df_clean.accounting_year == 2016))
        ]
        duplicate = pd.DataFrame(
            [
                [
                    6532,
                    "Firstsource Solutions",
                    "India",
                    np.nan,
                    np.nan,
                    2016,
                    "Operational control",
                    35.75,
                    "United Kingdom|India",
                    np.nan,
                    np.nan,
                    0.0,
                    0.3333333333333333,
                    np.nan,
                    np.nan,
                    np.nan,
                ]
            ],
            columns=df_clean.columns,
            index=[max(df_clean.index) + 1],
        )
        df_clean = pd.concat([df_clean, duplicate])

        df_clean = common_final_cleaning(df_clean)
        return df_clean
