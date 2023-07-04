import pandas as pd
import numpy as np


from functions.utils import dict_to_relevance


def get_df_year_clean_2015(path_raw_data):
    """
    Creates the clean datset for year 2015
    """
    year = 2015
    # Load useful sheets
    df_countries = pd.read_excel(
        path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx",
        sheet_name="CC0.3",
    )
    df_CF12 = pd.read_excel(
        path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx", sheet_name="CC8. Emissions Data"
    )
    df_CF3 = pd.read_excel(path_raw_data + "CDP_CC_emissions data_" + str(year) + ".xlsx", sheet_name="CC14.1")

    # year specific treatments
    df_CF12.loc[df_CF12.accounting_year.isna(), "accounting_year"] = [2014, 2014, 2014, 2014, 2014, 2014]

    # covered countries creation
    cols_temp = df_countries.columns
    df_countries["covered_countries"] = df_countries[cols_temp[-1]].fillna("") + df_countries[cols_temp[-2]].fillna("")
    unique_idx = df_countries.drop_duplicates("account_id").index
    countries_join = (
        df_countries.groupby("account_id")["covered_countries"].transform(lambda x: "; ".join(x)).to_frame()
    )
    countries_join = countries_join[countries_join.index.isin(unique_idx)].reset_index()
    df_covered_countries = countries_join.merge(df_countries.reset_index()[["account_id", "index"]], on="index")[
        ["account_id", "covered_countries"]
    ]

    # CF3 calculation
    count_rows = df_CF3.account_name.value_counts()
    df_CF3_filtered = df_CF3[df_CF3.account_name.isin(count_rows[count_rows == 17].index)]
    df_CF3_calc = (
        df_CF3_filtered.groupby(["account_id", "accounting_year"])[
            "CC14.1 C3 - Please account for your organization’s Scope 3 emissions, disclosing and explaining any exclusions - metric tonnes CO2e"
        ]
        .sum()
        .to_frame()
    )
    df_CF3_calc["CF3_relevance"] = np.zeros(len(df_CF3_calc))
    for i, mult_idx in enumerate(df_CF3_calc.index):
        df_2015_CF3_filtered_temp = df_CF3_filtered[
            (df_CF3_filtered.account_id == mult_idx[0]) & (df_CF3_filtered.accounting_year == mult_idx[1])
        ]
        dict_relevance = (
            df_2015_CF3_filtered_temp[
                "CC14.1 C2 - Please account for your organization’s Scope 3 emissions, disclosing and explaining any exclusions - Evaluation status"
            ]
            .value_counts()
            .to_dict()
        )
        df_CF3_calc.CF3_relevance.iloc[i] = dict_to_relevance(dict_relevance)

    # merge
    df_clean = df_CF12
    df_clean.columns = [
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

    df_clean = df_clean.merge(df_covered_countries[["account_id", "covered_countries"]], on="account_id")
    df_clean["unique_id"] = (
        df_clean["account_id"].astype(str) + "_" + df_clean["accounting_year"].astype(int).astype(str)
    )
    df_clean = df_clean.set_index(["account_id", "accounting_year"], drop=False)
    df_clean = df_clean[
        [
            "unique_id",
            "account_id",
            "account_name",
            "country",
            "ticker",
            "isin",
            "accounting_year",
            "boundary",
            "CDP_CF1",
            "CDP_CF2",
            "covered_countries",
        ]
    ]

    df_clean = df_clean.rename(columns={"CDP_CF2": "CDP_CF2_location"})

    df_clean["CDP_CF3"] = df_CF3_calc[df_CF3_calc.columns[0]]
    df_clean["CF3_relevance"] = df_CF3_calc["CF3_relevance"]

    df_clean["CDP_CF2_market"] = [np.nan for i in range(len(df_clean))]
    df_clean["activity"] = [np.nan for i in range(len(df_clean))]
    df_clean["sector"] = [np.nan for i in range(len(df_clean))]
    df_clean["industry"] = [np.nan for i in range(len(df_clean))]

    return df_clean


if __name__ == "__main__":
    path_raw_data = "raw_data/"
    df = get_df_year_clean_2015(path_raw_data, last_kept_year=np.nan)
    df.to_excel("temp_2015.xlsx")
