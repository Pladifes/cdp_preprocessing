import pandas as pd
import numpy as np

from tqdm import tqdm

from functions.utils import keep_main_boundary
from functions.get_2015 import get_df_year_clean_2015
from functions.get_2016 import get_df_year_clean_2016
from functions.get_2017 import get_df_year_clean_2017
from functions.get_2018 import get_df_year_clean_2018
from functions.get_2019 import get_df_year_clean_2019
from functions.get_2020 import get_df_year_clean_2020
from functions.get_2021 import get_df_year_clean_2021
from functions.get_2022 import get_df_year_clean_2022


def create_clean_dataset(df_cdp_concatenated):
    """
    Cleans the concatenated dataset from functions.the given years.
    """
    # some columns cleaning
    df_cdp_clean = df_cdp_concatenated
    df_cdp_clean["boundary"] = df_cdp_clean["boundary"].apply(keep_main_boundary)
    df_cdp_clean["CDP_CF2_location"] = (
        df_cdp_clean["CDP_CF2_location"].replace("Question not applicable", np.nan).astype(float)
    )
    df_cdp_clean["CDP_CF2_market"] = (
        df_cdp_clean["CDP_CF2_market"].replace("Question not applicable", np.nan).astype(float)
    )

    # for duplicated account x year, keep last available questionnaire
    df_cdp_clean["final_id"] = (
        df_cdp_clean["account_id"].astype(str)
        + "_"
        + df_cdp_clean["accounting_year"].astype(str)
        + "_"
        + df_cdp_clean["questionnaire_year"].astype(str)
    )
    lst_id_to_delete = []
    count_id = df_cdp_clean.unique_id.value_counts()

    for ids_in_double in count_id[count_id > 1].index:
        temp_ids = df_cdp_clean[df_cdp_clean.unique_id == ids_in_double]
        ids_to_delete = temp_ids[temp_ids.questionnaire_year != temp_ids.questionnaire_year.max()].final_id.tolist()
        lst_id_to_delete += ids_to_delete
    df_cdp_clean = df_cdp_clean[~(df_cdp_clean.final_id.isin(lst_id_to_delete))]

    # impute nan with first available observation for a given account for some columns
    df_cdp_clean = df_cdp_clean.reset_index(drop=True)
    cols_to_impute = [
        "isin",
        "ticker",
        "covered_countries",  # debatable
        "activity",
        "sector",
        "industry",
    ]

    for acc in tqdm(df_cdp_clean.account_id.unique()):  # 13 minutes
        df_acc = df_cdp_clean[df_cdp_clean.account_id == acc]
        for col in cols_to_impute:
            if df_acc[col].notna().any():
                curr_col_value = df_acc[col].loc[df_acc[col].first_valid_index()]
                df_cdp_clean.loc[(df_cdp_clean[col].isna()) & (df_cdp_clean.account_id == acc), col] = curr_col_value

    # Some country names handling
    df_cdp_clean = df_cdp_clean.replace("USA", "United States of America")
    df_cdp_clean = df_cdp_clean.replace("United Kingdom of Great Britain and Northern Ireland", "United Kingdom")

    return df_cdp_clean


def clean_CDP_year(path_raw_data, path_clean_data, year, save_years):
    """
    Loads or creates the clean CDP dataset for a given year.
    """
    # load base dataframes to merge
    try:
        df_year_clean = pd.read_excel(path_clean_data + "year.xlsx")

    except FileNotFoundError:
        dict_year_to_func = {
            2015: get_df_year_clean_2015,
            2016: get_df_year_clean_2016,
            2017: get_df_year_clean_2017,
            2018: get_df_year_clean_2018,
            2019: get_df_year_clean_2019,
            2020: get_df_year_clean_2020,
            2021: get_df_year_clean_2021,
            2022: get_df_year_clean_2022,
        }
        df_year_clean = dict_year_to_func[year](path_raw_data)

        df_year_clean["questionnaire_year"] = year

        if save_years == "csv":
            df_year_clean.to_csv("cdp_" + str(year) + "_dataset_clean.csv", index=False)
        elif save_years == "xlsx":
            df_year_clean.to_excel("cdp_" + str(year) + "_dataset_clean.xlsx", index=False)

    return df_year_clean


def create_CDP_clean_dataset(
    years=[year for year in range(2015, 2023)],
    path_raw_data="data/raw_data",
    path_clean_data="data/clean_data",
    save=False,
    save_years=False,
):
    """
    Creates the clean dataset with all available years.
    """
    lst_df_years = []
    for year in years:
        lst_df_years.append(clean_CDP_year(path_raw_data, path_clean_data, year, save_years))

    df_cdp_concatenated = pd.concat(lst_df_years)
    df_cdp_clean = create_clean_dataset(df_cdp_concatenated)

    if save == "csv":
        df_cdp_clean.to_csv("cdp_clean_dataset.csv", index=False)
    elif save == "xlsx":
        df_cdp_clean.to_excel("cdp_clean_dataset.xlsx", index=False)

    return df_cdp_clean
