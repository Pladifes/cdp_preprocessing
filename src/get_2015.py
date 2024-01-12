import numpy as np


from src.get_year import GetGivenYear
from src.get_year_functions import (
    load_useful_sheets,
    preprocess_covered_countries,
    common_final_cleaning,
    dict_to_relevance,
)


class Get2015(GetGivenYear):
    """
    Creates the clean datset for year 2015.

    This class is based on abstract class GetGivenYear.
    It uses generic functions from get_year_functions,
    as well as year specific methods/operations to format the data.
    The get_year_dataset method can be used to get the clean dataset.
    """

    def get_useful_sheets(self, path_raw_data):
        year = 2015
        return load_useful_sheets(path_raw_data, year)

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

    def preprocess_CF12(self, df_CF12):
        df_CF12["accounting_year"] = df_CF12["accounting_year"].fillna(2014)
        df_CF12.columns = [
            "program_name",
            "account_id",
            "project_year",
            "account_name",
            "country",
            "ticker",
            "isin",
            "row",
            "accounting_year",
            "boundary",
            "CDP_CF1",
            "CDP_CF2",
            "CF12_exhaustivity",
            "CF1_verification",
            "CF2_verification",
            "biologically_sequestration?",
            "biologically_sequestration_emissions",
        ]
        return df_CF12

    def get_year_dataset(self, path_raw_data):
        (df_countries, df_CF12, df_CF3) = self.get_useful_sheets(path_raw_data)
        df_covered_countries = self.get_covered_countries(df_countries)
        df_CF3_calc = self.get_scopes_3(df_CF3)
        df_clean = self.preprocess_CF12(df_CF12)

        # Merging part
        df_clean = df_clean.merge(
            df_covered_countries[["account_id", "covered_countries"]],
            on="account_id",
            how="left",
        )
        df_clean = df_clean.merge(
            df_CF3_calc,
            on=["account_id", "accounting_year"],
            how="left",
        )

        # Year specific treatments
        df_clean = df_clean.rename(columns={"CDP_CF2": "CDP_CF2_location"})
        df_clean["CDP_CF2_market"] = np.nan
        df_clean["activity"] = np.nan
        df_clean["sector"] = np.nan
        df_clean["industry"] = np.nan

        df_clean = common_final_cleaning(df_clean)
        return df_clean
