import os


from src.main_functions import create_CDP_clean_dataset


path_raw_data = os.path.join("data", "raw_data")
path_clean_data = os.path.join("data", "clean_data")
years = [year for year in range(2015, 2024)]
save_format = "xlsx"  # can be "xlsx", "csv" or False
save_years = "xlsx"  # can be "xlsx", "csv" or False

if __name__ == "__main__":
    create_CDP_clean_dataset(
        path_raw_data=path_raw_data,
        path_clean_data=path_clean_data,
        years=years,
        save_format=save_format,
        save_years=save_years,
    )
