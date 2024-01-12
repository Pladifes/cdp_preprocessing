def handle_duplicates(df_cdp_concatenated):
    """
    Handles duplicated records in the concatenated CDP dataset.

    Parameters:
    - df_cdp_concatenated (pandas.DataFrame): The concatenated CDP dataset containing
      potentially duplicated records.

    Returns:
    - pandas.DataFrame: Returns a DataFrame with duplicates handled by keeping the last available
      questionnaire values when several option are available for a given account and year.
    """
    df_cdp_concatenated["final_id"] = (
        df_cdp_concatenated["unique_id"].astype(str)
        + "_"
        + df_cdp_concatenated["questionnaire_year"].astype(str)
    )
    df_cdp_concatenated = df_cdp_concatenated.sort_values(by=["questionnaire_year"])
    df_cdp_concatenated = df_cdp_concatenated.drop_duplicates(
        subset="unique_id", keep="last"
    )
    del df_cdp_concatenated["final_id"]
    return df_cdp_concatenated


def missing_value_imputation(df_cdp_clean):
    """
    Imputes missing values with the last available observation for specific columns.

    Parameters:
    - df_cdp_clean (pandas.DataFrame): The DataFrame containing CDP data with potential missing values
      in certain columns.

    Returns:
    - pandas.DataFrame: Returns a DataFrame with missing values imputed for columns such as 'isin',
      'ticker', 'covered_countries', 'activity', 'sector', and 'industry'. The function replaces NaN
      values in these columns with the last available observation for each unique account,
      if such observations exist in the DataFrame.
    """
    df_cdp_clean = df_cdp_clean.reset_index(drop=True)
    cols_to_impute = [
        "isin",
        "ticker",
        "covered_countries",
        "activity",
        "sector",
        "industry",
    ]

    print("Imputing some missing categorical values: Start")
    for acc in df_cdp_clean.account_id.unique():
        df_acc = df_cdp_clean[df_cdp_clean.account_id == acc]
        for col in cols_to_impute:
            if df_acc[col].notna().any():
                curr_col_value = df_acc[col].loc[df_acc[col].last_valid_index()]
                df_cdp_clean.loc[
                    (df_cdp_clean[col].isna()) & (df_cdp_clean.account_id == acc), col
                ] = curr_col_value
    print("Imputing some missing categorical values: Done")
    return df_cdp_clean


def clean_country_names(df_cdp_clean):
    """
    Handles specific country names to use more generic equivalents.

    Parameters:
    - df_cdp_clean (pandas.DataFrame): The DataFrame containing CDP data with country names.

    Returns:
    - pandas.DataFrame: Returns a DataFrame with certain country names replaced with more generic ones.
    """
    df_cdp_clean = df_cdp_clean.replace("USA", "United States of America")
    df_cdp_clean = df_cdp_clean.replace(
        "United Kingdom of Great Britain and Northern Ireland", "United Kingdom"
    )
    return df_cdp_clean
