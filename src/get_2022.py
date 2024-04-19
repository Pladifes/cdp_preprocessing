from src.get_year import GetGivenYear
from src.get_year_functions import (
    load_useful_sheets,
    preprocess_accounting_years,
    calculate_relevance,
    attribute_CF3_to_last_year,
    common_final_cleaning,
)


class Get2022(GetGivenYear):
    """
    Creates the clean datset for year 2022.

    This class is based on abstract class GetGivenYear.
    It uses generic functions from get_year_functions,
    as well as year specific methods/operations to format the data.
    The get_year_dataset method can be used to get the clean dataset.
    """

    def get_useful_sheets(self, path_raw_data):
        year = 2022
        return load_useful_sheets(year, path_raw_data)

    def get_all_accounting_year(self, df_years):
        return preprocess_accounting_years(df_years)

    def get_scopes_3(self, df_CF3):
        col_metric = "C6.5_C2_Account for your organization’s gross global Scope 3 emissions, disclosing and explaining any exclusions. - Emissions in reporting year (metric tons CO2e)"
        df_CF3[col_metric] = (
            df_CF3[col_metric].replace("Question not applicable", 0).astype(float)
        )
        df_CF3_calc = (
            df_CF3.groupby("Account number")[col_metric].sum().to_frame("CDP_CF3")
        )
        col_evaluation = "C6.5_C1_Account for your organization’s gross global Scope 3 emissions, disclosing and explaining any exclusions. - Evaluation status"
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
            df_boundaries,
            df_CF1,
            df_CF2,
            df_CF3,
        ) = self.get_useful_sheets(path_raw_data)
        df_years_filtered = self.get_all_accounting_year(df_years)
        df_CF3_calc = self.get_scopes_3(df_CF3)

        # Merging part
        df_clean = df_years_filtered
        df_clean = df_clean.merge(df_base, on="Account number", how="left")
        df_clean = df_clean.merge(
            df_boundaries[
                [
                    "Account number",
                    "C0.5_Select the option that describes the reporting boundary for which climate-related impacts on your business are being reported. Note that this option should align with your chosen approach for consolidating your GHG inventory.",
                ]
            ],
            on="Account number",
            how="left",
        )
        df_clean = df_clean.merge(
            df_countries[
                [
                    "Account number",
                    "C0.3_Select the countries/areas in which you operate.",
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
            on=["Account number", "Row"],
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
            on=["Account number", "Row"],
            how="left",
        )
        df_clean = df_clean.merge(
            df_CF3_calc.reset_index()[
                [
                    "Account number",
                    "CDP_CF3",
                    "CF3_relevance",
                ]
            ],
            on="Account number",
            how="left",
        )

        # Year specific treatments
        df_clean = common_final_cleaning(df_clean)
        df_clean = attribute_CF3_to_last_year(df_clean)
        return df_clean
