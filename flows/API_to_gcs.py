#!/usr/bin/env python
# coding: utf-8
import argparse
import pandas as pd
import weather_API as weather_API

from sqlalchemy import create_engine
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect_gcp.cloud_storage import GcsBucket
from pathlib import Path

@task(retries = 3)
def extract_data(location: dict) -> pd.DataFrame:
	df = weather_API.get_data_from_api(location)
	return df

@task(log_prints=True)
def transform_data(df):
	print(f'\npre: nan Count:\n{df.isnull().sum()}')
	df_clean = df.dropna()
	print(f'\npost: nan Count:\n{df_clean.isnull().sum()}')
	return df_clean

@task()
def check_hourly_continuity(df: pd.DataFrame, date_column: str = 'date'):
    """
    Checks if the 'date' column in a DataFrame has a consistent hourly frequency.

    Args:
        df: The pandas DataFrame with a datetime column.
        date_column: The name of the datetime column (default is 'date').

    Returns:
        None. Prints messages indicating any deviations from the hourly frequency.
    """
    # Make sure the 'date' column is actually in datetime format
    df.loc[:, date_column] = pd.to_datetime(df[date_column])

    # Calculate the time difference between consecutive rows
    time_diffs = df[date_column].diff()

    # The expected difference is one hour
    expected_delta = pd.Timedelta(hours=1)

    # Check for any differences that are not equal to one hour
    for i, diff in time_diffs[1:].items(): # Start from the second row
        if diff != expected_delta:
            print(f"Potential missing or extra data around index {i}: Difference is {diff}")

@task(log_prints=True)
def store_data(df, table_name):
	connection_block = SqlAlchemyConnector.load("postgres-connector")
	with connection_block.get_connection(begin=False) as engine: 
		print(df.to_sql(name=f'{table_name}', con=engine, if_exists='append'))
		
@task()
def store_local(df, town):
	"""store dataframe locally as parquet file"""
	path = Path(f"data/{town}_data.parquet")
	df.to_parquet(path, compression = "gzip")
	return path

@task()
def write_gcs(path):
	gcs_block = GcsBucket.load("gcs-connector")
	gcs_block.upload_from_path(
		from_path=path,
		to_path=path
	)
	return

@task()
def load_existing_gcs(path: str) -> pd.DataFrame:
    gcs_block = GcsBucket.load("gcs-connector")
    local_path = Path("data/prev_data.parquet")
    local_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure data/ exists

    try:
        gcs_block.download_object_to_path(
            from_path=path,
            to_path=str(local_path)
        )
        return pd.read_parquet(local_path)
    except Exception as e:
        print(f"Could not load existing data: {e}")
        return pd.DataFrame()


@task()
def filter_new_entries(new_df: pd.DataFrame, old_df: pd.DataFrame) -> pd.DataFrame:
	if old_df.empty:
		return new_df
	return new_df[~new_df['date'].isin(old_df['date'])]

@task()
def etl_web_to_gcs(town: str, location: dict) -> None:
	gcs_path = Path(f"data/{town}_data.parquet")

	# ETL steps
	df_raw = extract_data(location)
	df_clean = transform_data(df_raw)
	hourly_discontinuity = check_hourly_continuity(df_clean)
	if hourly_discontinuity:
		print("Missing Data or error in format.")
		return

	df_existing = load_existing_gcs(gcs_path)
	df_new = filter_new_entries(df_clean, df_existing)

	if df_new.empty:
		print("No new data to ingest.")
		return

	# Proceed with storing only new data
	df_updated = pd.concat([df_existing, df_new]).drop_duplicates(subset='date').sort_values('date')
	
	store_data(df_new, town)  # <- only load *new* data into DB
	path = store_local(df_updated, town)
	write_gcs(path)

@flow()
def etl_parent_flow():

	locations = {
		"Wuppertal": {"latitude": 51.26, "longitude": 7.15,},
		"Bruegge": {"latitude": 51.22, "longitude": 3.22,},
		"Groningen": {"latitude": 53.22, "longitude": 6.57,},
		"Erfurt": {"latitude": 50.98, "longitude": 11.03,},
		"Saarbruecken": {"latitude": 49.23, "longitude": 7.00,},
	}

	for town, location in locations.items():
		etl_web_to_gcs(town, location)

if __name__ == '__main__':
	etl_parent_flow()