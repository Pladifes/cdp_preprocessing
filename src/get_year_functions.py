import os


import numpy as np
import pandas as pd


from datetime import datetime


def load_useful_sheets(year, path_raw_data):
    """
    Loads relevant sheets from the CDP_CC_emissions_year.xlsx data for a given year.

    Parameters:
    - year (int): The year for which the relevant data sheets are to be loaded.
    - path_raw_data (str): Path to the raw data directory. Defaults to data/raw_data.

    Returns:
    - tuple: Depending on the year provided, returns a tuple containing DataFrames for
      specific sheets from the CDP_CC_emissions data. For years 2015 to 2022, returns
      a tuple with DataFrames for different sheets related to emissions and summary
      data (reporting years, countries, boundaries).
    """
    file_path = os.path.join(path_raw_data, f"CDP_CC_emissions data_{year}.xlsx")
    if year in [2015, 2016, 2017]:
        df_countries = pd.read_excel(file_path, sheet_name="CC0.3")
        df_CF1 = pd.read_excel(file_path, sheet_name="CC8. Emissions Data")
        df_CF3 = pd.read_excel(file_path, sheet_name="CC14.1")
        if year == 2015:
            return (df_countries, df_CF1, df_CF3)
        else:
            df_CF2 = pd.read_excel(file_path, sheet_name="CC8.3a")
            return (df_countries, df_CF1, df_CF2, df_CF3)

    elif year in [2018, 2019, 2020, 2021, 2022]:
        if year == 2022:
            df_base = pd.read_excel(file_path, sheet_name="Summary Data")
        else:
            df_base = pd.read_excel(file_path, sheet_name="C0 - Introduction")

        df_years = pd.read_excel(file_path, sheet_name="C0.2")

        try:
            df_countries = pd.read_excel(file_path, sheet_name="C0.3")
        except ValueError:
            df_countries = None

        try:
            df_boundaries = pd.read_excel(file_path, sheet_name="C0.5")
        except ValueError:
            df_boundaries = None

        df_CF1 = pd.read_excel(file_path, sheet_name="C6.1")
        df_CF2 = pd.read_excel(file_path, sheet_name="C6.3")
        df_CF3 = pd.read_excel(file_path, sheet_name="C6.5")

        dict_to_return = {
            2018: (df_base, df_years, df_countries, df_CF1, df_CF2, df_CF3),
            2019: (df_base, df_years, df_countries, df_CF1, df_CF2, df_CF3),
            2020: (df_base, df_years, df_CF1, df_CF2, df_CF3),
            2021: (df_base, df_years, df_CF1, df_CF2, df_CF3),
            2022: (
                df_base,
                df_years,
                df_countries,
                df_boundaries,
                df_CF1,
                df_CF2,
                df_CF3,
            ),
        }
    return dict_to_return[year]


def preprocess_covered_countries(df_countries):
    """
    Preprocesses covered countries data in a DataFrame.
    Data can the be loaded in lists using: lambda x: json.loads(x)

    Parameters:
    - df_countries (pandas.DataFrame): A DataFrame containing information about covered countries,
      potentially with multiple columns.

    Returns:
    - pandas.DataFrame: Returns a DataFrame containing aggregated covered countries information
      grouped by 'account_id'. The function concatenates country information from the last two columns
      ('covered_countries') for each row using a delimiter ', ', fills NaN values with empty strings,
      and aggregates this information for each 'account_id', resulting in a DataFrame with 'account_id'
      and concatenated 'covered_countries' information.
    """
    df_countries["covered_countries"] = df_countries.apply(
        lambda x: "".join(filter(None, x[-2:].fillna(""))), axis=1
    )
    df_covered_countries = (
        df_countries.groupby("account_id")["covered_countries"]
        .agg('","'.join)
        .reset_index()
    )
    df_covered_countries["covered_countries"] = (
        df_covered_countries.covered_countries.apply(lambda x: f'["{x}"]')
    )
    df_covered_countries["covered_countries"] = df_covered_countries[
        "covered_countries"
    ].replace('[""]', "[]")
    return df_covered_countries


def str_to_accounting_year(reporting_date):
    """
    Get the accounting year based on the end date.

    Parameters:
    - reporting_date (str): A numeric date in the format YYYYMMDD.

    Returns:
    - year (int): The accounting year derived from the reporting date. Returns np.nan for invalid or out-of-range dates.
    """
    try:
        # Convert the numeric date to a string and then to a datetime object
        date = datetime.strptime(str(reporting_date), "%Y%m%d")
    except ValueError:
        return np.nan

    year = date.year - 1 if date.month < 7 else date.year

    if year < 2009:
        # print("error, data anterior to 2009")
        return np.nan
    elif year > 2024:
        # print("error, data posterior to 2024")
        return np.nan
    else:
        return year


def preprocess_accounting_years(df_years):
    """
    Preprocesses accounting year data from a DataFrame by filtering and formatting date columns.

    Parameters:
    - df_years (pandas.DataFrame): A DataFrame containing accounting year data with columns
      specifying start and end dates for reporting data.

    Returns:
    - pandas.DataFrame: Returns a preprocessed DataFrame where rows with 'Question not applicable'
      or NaN values in start_date or end_date columns are filtered out. The start_date and end_date
      columns are converted to yyyyMMdd string format, and a new 'accounting_year' column is added
      containing the derived accounting years using the 'str_to_accounting_year' function.
    """
    start_date_col = "C0.2_C1_State the start and end date of the year for which you are reporting data. - Start date"
    end_date_col = "C0.2_C2_State the start and end date of the year for which you are reporting data. - End date"

    # Filter out rows where start_date or end_date is 'Question not applicable' or NaN
    df_years_filtered = df_years[
        (df_years[start_date_col] != "Question not applicable")
        & (df_years[end_date_col] != "Question not applicable")
    ].dropna()

    # Convert date columns to yyyyMMdd string format
    df_years_filtered["start_date"] = (
        pd.to_datetime(df_years_filtered[start_date_col])
        .dt.strftime("%Y%m%d")
        .astype("int64")
    )
    df_years_filtered["end_date"] = (
        pd.to_datetime(df_years_filtered[end_date_col])
        .dt.strftime("%Y%m%d")
        .astype("int64")
    )

    # Apply str_to_accounting_year to the end_date column
    df_years_filtered["accounting_year"] = df_years_filtered["end_date"].apply(
        str_to_accounting_year
    )
    return df_years_filtered.reset_index(drop=True)


def dict_to_relevance(dict_relevance):
    """
    Derives the relevance of disclosed scope 3 based on a specific ratio:
    [reported scope 3 categories] / [relevant scope 3 categories].
    This metric, designed by Thibaud BARREAU, doesn't correlate with existing metrics.

    Parameters:
    - dict_relevance (dict): A dictionary containing counts of different scope 3 categories,
      categorized as 'Relevant, calculated', 'Not relevant, calculated', 'Not evaluated',
      'Relevant, not yet calculated', 'Question not applicable'.

    Returns:
    - (float): The derived relevance ratio, calculated as the sum of 'Relevant, calculated'
      and 'Not relevant, calculated' categories divided by the sum of all relevant categories.
      Returns 0 if the denominator is zero or if NaN values are encountered in the calculations,
      signifying no relevance based on the provided data.
    """
    if sum(dict_relevance.values()) == 0:
        return 0  # No explanations so considered not relevant

    relevance_numerator = dict_relevance.get(
        "Relevant, calculated", 0
    ) + dict_relevance.get("Not relevant, calculated", 0)

    relevance_denominator = (
        dict_relevance.get("Not evaluated", 0)
        # + dict_relevance.get("Question not applicable", 0)
        + dict_relevance.get("Relevant, calculated", 0)
        + dict_relevance.get("Relevant, not yet calculated", 0)
        + dict_relevance.get("Not relevant, calculated", 0)
    )

    # Check for NaN in numerator or denominator
    if (
        pd.isna(relevance_numerator)
        or pd.isna(relevance_denominator)
        or relevance_denominator == 0
    ):
        return 0  # Handle NaN or zero denominator

    return relevance_numerator / relevance_denominator


def calculate_relevance(group, col):
    """
    Calculates the relevance ratio based on counts of values in a specific column within a group.

    Parameters:
    - group (pandas.DataFrame): A group or subset of a DataFrame containing relevant data.
    - col (str): The column name in the DataFrame used to calculate relevance based on value counts.

    Returns:
    - float: The relevance ratio derived from the value counts of the specified column within the group.
      Returns the relevance ratio calculated using the 'dict_to_relevance' function,
      which processes the counts of different values in the specified column.
    """
    dict_relevance = group[col].value_counts().to_dict()
    return dict_to_relevance(dict_relevance)


def attribute_CF3_to_last_year(df_clean):
    """
    Attributes NaN values to 'CDP_CF3' and 'CF3_relevance' columns in a DataFrame
    based on accounting year for each unique account ID except for the last year.

    Parameters:
    - df_clean (pandas.DataFrame): A dataframe with 'account_id' and 'accounting_year', 'CDP_CF3' and 'CF3_relevance'
    columns, that need to be modified.

    Returns:
    - pandas.DataFrame: Returns the modified DataFrame where for each account ID,
      all entries except those corresponding to the last accounting year are assigned
      NaN values in 'CDP_CF3' and 'CF3_relevance' columns.
    """
    occurrences = df_clean.account_id.value_counts()
    no_unique_corpo = df_clean[
        df_clean.account_id.isin(occurrences[occurrences > 1].index)
    ]
    for idd in no_unique_corpo.account_id:
        last_year = df_clean[df_clean.account_id == idd].accounting_year.max()
        df_clean.loc[
            (df_clean.accounting_year != last_year) & (df_clean.account_id == idd),
            "CDP_CF3",
        ] = np.nan
        df_clean.loc[
            (df_clean.accounting_year != last_year) & (df_clean.account_id == idd),
            "CF3_relevance",
        ] = np.nan
    return df_clean


def keep_main_boundary(boundary):
    """
    Filter non-standard GHG reporting boundaries.

    Parameters:
    - boundary (str): The boundary type to be checked.

    Returns:
    - str or np.nan: Returns the input boundary type if it's one of
    ["Operational control", "Financial control", "Equity share"], otherwise returns np.nan.
    """
    if boundary in ["Operational control", "Financial control", "Equity share"]:
        return boundary
    else:
        return np.nan


def common_final_cleaning(df_clean):
    """
    Performs columns filtering and final cleaning on a DataFrame.

    Parameters:
    - df_clean (pandas.DataFrame): The input DataFrame containing various columns.

    Returns:
    - pandas.DataFrame: Returns a modified DataFrame after performing specific cleaning operations.
    """
    # Final formating (columns renaming and filtering)
    df_clean = df_clean.rename(
        columns={
            "Country/Areas_x": "country",
            "Primary activity_x": "activity",
            "Primary sector_x": "sector",
            "Primary industry_x": "industry",
            "tickers": "ticker",
            "Account number": "account_id",
            "Organization": "account_name",
            "Organization_x": "account_name",
            "Country": "country",
            "Primary activity": "activity",
            "Primary sector": "sector",
            "Primary industry": "industry",
            "ISINs": "isin",
            "Tickers": "ticker",
            "C0.3_Select the countries/areas in which you operate.": "covered_countries",
            "C0.5_Select the option that describes the reporting boundary for which climate-related impacts on your business are being reported. Note that this option should align with your consolidation approach to your Scope 1 and Scope 2 greenhouse gas inventory.": "boundary",
            "C0.5_Select the option that describes the reporting boundary for which climate-related impacts on your business are being reported. Note that this option should align with your chosen approach for consolidating your GHG inventory.": "boundary",
            "C0.3_Select the countries/regions for which you will be supplying data.": "covered_countries",
            "C6.1_C1_What were your organization’s gross global Scope 1 emissions in metric tons CO2e? - Gross global Scope 1 emissions (metric tons CO2e)": "CDP_CF1",
            "C6.3_C1_What were your organization’s gross global Scope 2 emissions in metric tons CO2e? - Scope 2, location-based": "CDP_CF2_location",
            "C6.3_C2_What were your organization’s gross global Scope 2 emissions in metric tons CO2e? - Scope 2, market-based (if applicable)": "CDP_CF2_market",
        }
    )
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
    df_clean["unique_id"] = (
        df_clean["account_id"].astype(str)
        + "_"
        + df_clean["accounting_year"].astype(int).astype(str)
    )

    # Final cleaning
    df_clean = df_clean.dropna(subset=["account_id", "accounting_year"])
    df_clean["boundary"] = df_clean["boundary"].apply(keep_main_boundary)
    for col in ["CDP_CF2_location", "CDP_CF2_market"]:
        df_clean[col] = (
            df_clean[col].replace("Question not applicable", np.nan).astype(float)
        )
    df_clean = df_clean.reset_index(drop=True)
    return df_clean
