import pandas as pd
import numpy as np


from functions.utils import dict_to_relevance, get_accounting_year


def get_df_year_clean_2021(path_raw_data):
    """
    Creates the clean datset for year 2021
    """
    year = 2021
    # Load useful sheets
    df_base = pd.read_excel(
        path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx",
        sheet_name="C0 - Introduction",
    )
    df_years = pd.read_excel(path_raw_data + "CDP_CC_emissions data_2021.xlsx", sheet_name="C0.2")

    df_CF1 = pd.read_excel(path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx", sheet_name="C6.1")
    df_CF2 = pd.read_excel(path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx", sheet_name="C6.3")

    df_CF3 = pd.read_excel(path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx", sheet_name="C6.5")

    # accounting year derivation
    start_date = "C0.2_C1_State the start and end date of the year for which you are reporting data. - Start date"
    end_date = "C0.2_C2_State the start and end date of the year for which you are reporting data. - End date"
    df_years_filtered = df_years[~(df_years[start_date] == "Question not applicable")].dropna()
    df_years_filtered = df_years_filtered[~(df_years_filtered[end_date] == "Question not applicable")].dropna()
    df_years_filtered["start_date"] = df_years_filtered[start_date].apply(lambda x: int(x[:4] + x[5:7] + x[8:10]))
    df_years_filtered["end_date"] = df_years_filtered[end_date].apply(lambda x: int(x[:4] + x[5:7] + x[8:10]))
    df_years_filtered["accounting_year"] = df_years_filtered["end_date"].apply(get_accounting_year)

    # CF3 calculation
    df_CF3["CF3"] = (
        df_CF3[
            "C6.5_C2_Account for your organization’s gross global Scope 3 emissions, disclosing and explaining any exclusions. - Metric tonnes CO2e"
        ]
        .replace("Question not applicable", 0)
        .astype(float)
    )
    df_CF3_calc = df_CF3.groupby(["Account number"])["CF3"].sum().to_frame()

    df_CF3_calc["CF3_relevance"] = np.zeros(len(df_CF3_calc))
    for i, index in enumerate(df_CF3_calc.index):
        df_CF3_filtered_temp = df_CF3[df_CF3["Account number"] == index]

        dict_relevance = (
            df_CF3_filtered_temp[
                "C6.5_C2_Account for your organization’s gross global Scope 3 emissions, disclosing and explaining any exclusions. - Metric tonnes CO2e"
            ]
            .value_counts()
            .to_dict()
        )
        df_CF3_calc.CF3_relevance.iloc[i] = dict_to_relevance(dict_relevance)

    # merge
    df_clean = df_years_filtered

    df_clean = df_clean.merge(
        df_base[
            [
                "Account number",
                "C0.5_Select the option that describes the reporting boundary for which climate-related impacts on your business are being reported. Note that this option should align with your chosen approach for consolidating your GHG inventory.",
            ]
        ],
        on="Account number",
    )

    df_clean["id_merge_row"] = df_clean["Account number"].astype(str) + "_" + df_clean["Row"].astype(str)
    df_CF1["id_merge_row"] = df_CF1["Account number"].astype(str) + "_" + df_CF1["Row"].astype(str)
    df_CF2["id_merge_row"] = df_CF2["Account number"].astype(str) + "_" + df_CF2["Row"].astype(str)

    df_clean = df_clean.merge(
        df_CF1[
            [
                "C6.1_C1_What were your organization’s gross global Scope 1 emissions in metric tons CO2e? - Gross global Scope 1 emissions (metric tons CO2e)",
                "id_merge_row",
            ]
        ],
        on="id_merge_row",
    )
    df_clean = df_clean.merge(
        df_CF2[
            [
                "id_merge_row",
                "C6.3_C1_What were your organization’s gross global Scope 2 emissions in metric tons CO2e? - Scope 2, location-based",
                "C6.3_C2_What were your organization’s gross global Scope 2 emissions in metric tons CO2e? - Scope 2, market-based (if applicable)",
            ]
        ],
        on="id_merge_row",
    )

    df_clean = df_clean.merge(
        df_CF3_calc.reset_index()[
            [
                "Account number",
                "CF3",
                "CF3_relevance",
            ]
        ],
        on="Account number",
    )
    df_clean.columns = [
        "account_id",
        "account_name",
        "country",
        "public",
        "response_date",
        "activity",
        "sector",
        "industry",
        "primary sector",
        "row",
        "row_name",
        "start_date_raw",
        "end_date_raw",
        "past_data",
        "number_of_years",
        "start_date",
        "end_date",
        "accounting_year",
        "boundary",
        "id_merge_row",
        "CDP_CF1",
        "CDP_CF2_location",
        "CDP_CF2_market",
        "CDP_CF3",
        "CF3_relevance",
    ]

    df_clean["covered_countries"] = np.nan
    df_clean["isin"] = np.nan
    df_clean["ticker"] = np.nan
    df_clean = df_clean[
        [
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
        ]
    ]

    df_clean["unique_id"] = df_clean["account_id"].astype(str) + "_" + df_clean["accounting_year"].astype(str)

    a = df_clean.account_id.value_counts()
    no_unique_corpo = df_clean[df_clean.account_id.isin(a[a > 1].index)]
    for idd in no_unique_corpo.account_id:
        last_year = df_clean[df_clean.account_id == idd].accounting_year.max()
        df_clean.loc[(df_clean.accounting_year != last_year) & (df_clean.account_id == idd), "CDP_CF3"] = np.nan
        df_clean.loc[(df_clean.accounting_year != last_year) & (df_clean.account_id == idd), "CF3_relevance"] = np.nan

    return df_clean


if __name__ == "__main__":
    path_raw_data = "raw_data/"
    df = get_df_year_clean_2021(path_raw_data)
    df.to_excel("temp_2021.xlsx")
