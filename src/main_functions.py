import os


import pandas as pd


from src.get_2015 import Get2015
from src.get_2016 import Get2016
from src.get_2017 import Get2017
from src.get_2018 import Get2018
from src.get_2019 import Get2019
from src.get_2020 import Get2020
from src.get_2021 import Get2021
from src.get_2022 import Get2022
from src.get_2023 import Get2023
from src.utils import handle_duplicates, missing_value_imputation, clean_country_names


def clean_CDP_year(path_raw_data, path_clean_data, year, save_years):
    """
    Loads or creates the clean CDP dataset for a given year.

    Parameters:
    - path_raw_data (str): The path to the directory where raw datasets are stored.
    - path_clean_data (str): The path to the directory where cleaned datasets are stored.
    - year (int): The specific year for which the dataset is being processed.
    - save_years (str): Flag indicating whether to save the cleaned dataset for the specific year.
      If "csv" or "xlsx", saves the file in CSV or EXCEL format.

    Returns:
    - pandas.DataFrame: Returns the cleaned dataset for the specified year as a DataFrame.
      If the dataset is successfully loaded or created, returns the DataFrame. If the year is not present
      in predefined classes returns an empty DataFrame.
    """
    try:
        print(year, "- trying to load pre cleaned dataset")
        df_year_clean = pd.read_excel(
            os.path.join(path_clean_data, f"cdp_clean_{year}.xlsx")
        )
        print(year, "- pre cleaned dataset successfully loaded")

    except FileNotFoundError:
        print(year, "- loading of pre cleaned dataset failed, reconstructing it")
        dict_year_to_func = {
            2015: Get2015(),
            2016: Get2016(),
            2017: Get2017(),
            2018: Get2018(),
            2019: Get2019(),
            2020: Get2020(),
            2021: Get2021(),
            2022: Get2022(),
            2023: Get2023(),
        }
        try:
            df_year_clean = dict_year_to_func[year].get_year_dataset(path_raw_data)

        except KeyError:
            print(year, " is not in predifined classes, please implement a new one.")
            df_empty = pd.DataFrame(
                [],
                columns=[
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
                ],
            )
            return df_empty

        df_year_clean["questionnaire_year"] = year
        if save_years:
            file_path = os.path.join(path_clean_data, f"cdp_clean_{year}.{save_years}")
            dict_attr = {"csv": "csv", "xlsx": "excel"}
            getattr(df_year_clean, f"to_{dict_attr[save_years]}")(
                file_path, index=False
            )
            print("Saving cleaned dataset: Done")

    return df_year_clean


def create_CDP_clean_dataset(
    path_raw_data=os.path.join("data", "raw_data"),
    path_clean_data=os.path.join("data", "clean_data"),
    years=[year for year in range(2015, 2023)],
    save_years=False,
    save_format=False,
):
    """
    Creates a clean dataset by aggregating and cleaning data from multiple years.

    Parameters:
    - path_raw_data (str, optional): Path to the raw data directory. Defaults to data/raw_data.
    - path_clean_data (str, optional): Path to the clean data directory. Defaults to data/clean_data.
    - years (list, optional): A list of years to process. Defaults to range from 2015 to 2022.
    - save_years (bool or str, optional): Flag indicating whether to save separate years' datasets.
      Defaults to False. If "csv" or "xlsx", saves the file in CSV or EXCEL format.
    - save_format (bool or str, optional): Flag indicating whether to save separate years' datasets.
      Defaults to False. If "csv" or "xlsx", saves the file in CSV or EXCEL format.

    Returns:
    - pandas.DataFrame: Returns a cleaned and concatenated DataFrame comprising data from
      specified years (default: 2015 to 2022). If specified, the resulting DataFrame is also saved
      as a CSV or Excel file based on the 'save' parameter.
    """
    print("Loading of year specific datasets: Start")
    lst_df_years = []
    for year in years:
        lst_df_years.append(
            clean_CDP_year(path_raw_data, path_clean_data, year, save_years)
        )
    print("Loading of year specific datasets: Done")
    
    print("Cleaning of the concatenated dataset: Start")
    df_cdp_concatenated = pd.concat(lst_df_years)
    df_cdp_clean = handle_duplicates(df_cdp_concatenated)
    df_cdp_clean = missing_value_imputation(df_cdp_clean)
    df_cdp_clean = clean_country_names(df_cdp_clean)
    df_cdp_clean = df_cdp_clean.reset_index(drop=True)
    print("Cleaning of the concatenated dataset: Done")

    if save_format:
        print("Saving cleaned dataset: Start")
        file_path = os.path.join(path_clean_data, f"cdp_clean_dataset.{save_format}")
        dict_attr = {"csv": "csv", "xlsx": "excel"}
        getattr(df_cdp_clean, f"to_{dict_attr[save_format]}")(file_path, index=False)
        print("Saving cleaned dataset: Done")

    return df_cdp_clean
