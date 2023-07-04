from functions.main_functions import create_CDP_clean_dataset


path_raw_data = "data/raw_data/"
path_clean_data = "data/clean_data/"
years = [year for year in range(2015, 2023)]
save = True
save_years = True

if __name__ == "__main__":
    create_CDP_clean_dataset(
        path_raw_data=path_raw_data, path_clean_data=path_clean_data, years=years, save=save, save_years=save_years
    )
