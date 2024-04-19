from src.get_year import GetGivenYear
from src.get_year_functions import (
    load_useful_sheets,
    preprocess_accounting_years,
    calculate_relevance,
    attribute_CF3_to_last_year,
    common_final_cleaning,
)


class Get2018(GetGivenYear):
    """
    Creates the clean datset for year 2018.

    This class is based on abstract class GetGivenYear.
    It uses generic functions from get_year_functions,
    as well as year specific methods/operations to format the data.
    The get_year_dataset method can be used to get the clean dataset.
    """

    def get_useful_sheets(self, path_raw_data):
        year = 2018
        return load_useful_sheets(year, path_raw_data)

    def get_all_accounting_year(self, df_years):
        return preprocess_accounting_years(df_years)

    def get_scopes_3(self, df_CF3):
        df_CF3_calc = (
            df_CF3.groupby("Account number")[
                "C6.5_C2_Account for your organization’s Scope 3 emissions, disclosing and explaining any exclusions. - Metric tonnes CO2e"
            ]
            .sum()
            .to_frame("CDP_CF3")
        )
        col_evaluation = "C6.5_C1_Account for your organization’s Scope 3 emissions, disclosing and explaining any exclusions. - Evaluation status"
        df_CF3_calc["CF3_relevance"] = (
            df_CF3.groupby("Account number")
            .apply(lambda x: calculate_relevance(x, col_evaluation))
            .values
        )
        return df_CF3_calc

    def get_year_dataset(self, path_raw_data):
        (
            df_base,
            df_years,
            df_countries,
            df_CF1,
            df_CF2,
            df_CF3,
        ) = self.get_useful_sheets(path_raw_data)
        df_years_filtered = self.get_all_accounting_year(df_years)
        df_CF3_calc = self.get_scopes_3(df_CF3)

        # Merging part
        df_clean = df_years_filtered
        df_clean = df_clean.merge(
            df_base[
                [
                    "Account number",
                    "C0.5_Select the option that describes the reporting boundary for which climate-related impacts on your business are being reported. Note that this option should align with your consolidation approach to your Scope 1 and Scope 2 greenhouse gas inventory.",
                ]
            ],
            on="Account number",
            how="left",
        )
        df_clean = df_clean.merge(
            df_countries[
                [
                    "Account number",
                    "C0.3_Select the countries/regions for which you will be supplying data.",
                ]
            ],
            on="Account number",
            how="left",
        )
        df_clean = df_clean.merge(
            df_CF1[
                [
                    "C6.1_C1_What were your organization’s gross global Scope 1 emissions in metric tons CO2e? - Gross global Scope 1 emissions (metric tons CO2e)",
                    "Account number",
                    "Row",
                ]
            ],
            on=["Row", "Account number"],
            how="left",
        )
        df_clean = df_clean.merge(
            df_CF2[
                [
                    "Account number",
                    "Row",
                    "C6.3_C1_What were your organization’s gross global Scope 2 emissions in metric tons CO2e? - Scope 2, location-based",
                    "C6.3_C2_What were your organization’s gross global Scope 2 emissions in metric tons CO2e? - Scope 2, market-based (if applicable)",
                ]
            ],
            on=["Row", "Account number"],
            how="left",
        )
        df_clean = df_clean.merge(df_CF3_calc, on="Account number", how="left")

        # Year specific treatments
        df_clean["id_merge_row"] = (
            df_clean["Account number"].astype(str)
            + "_"
            + df_clean["Row"].fillna(0).astype(int).astype(str)
        )
        df_clean = df_clean.drop(
            df_clean[
                df_clean.id_merge_row.isin(
                    [
                        "22698_4",
                        "1408_2",
                        "2191_4",
                        "3435_2",
                        "5574_2",
                        "29824_2",
                        "8051_4",
                        "8663_2",
                        "23024_2",
                        "22566_1",
                        "18436_1",
                        "18436_2",
                        "19184_2",
                    ]
                )
            ].index
        )
        df_clean.loc[df_clean["Account number"] == 22698, "accounting_year"] = [
            2017,
            2016,
            2015,
        ]
        df_clean.loc[df_clean["Account number"] == 8051, "accounting_year"] = [
            2017,
            2016,
            2015,
        ]

        df_clean = common_final_cleaning(df_clean)
        df_clean = attribute_CF3_to_last_year(df_clean)
        return df_clean
