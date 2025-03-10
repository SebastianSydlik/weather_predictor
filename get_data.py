#!/usr/bin/env python
# coding: utf-8
import openmeteo_requests
import argparse
import requests_cache
import pandas as pd

from retry_requests import retry
from sqlalchemy import create_engine
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector

@task(log_prints=True)
def main(params):
	user = params.user
	password = params.password
	host = params.host
	port = params.port
	db = params.db
	table_name = params.table_name

	df_raw = get_data_from_api()
	df = transform_data(df_raw)
	# connection_block = SqlAlchemyConnector.load("sql0")
	# with connection_block.get_connection(begin=False) as engine: 
	engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
	engine.connect()
	print(df.to_sql(name=f'{table_name}', con=engine, if_exists='replace'))

@task(log_prints=True)
def transform_data(df):
	print(f'\npre: nan Count:\n{df.isnull().sum()}')
	df_clean = df.dropna()
	print(f'\npost: nan Count:\n{df_clean.isnull().sum()}')
	return df_clean

@task(log_prints=True, retries=3)
def get_data_from_api():
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://archive-api.open-meteo.com/v1/archive"
	params = {
		"latitude": 51.26,
		"longitude": 7.15,
		"start_date": "2025-01-01",
		"end_date": "2025-03-06",
		"hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "weather_code", "cloud_cover", "wind_speed_100m"],
		"timezone": "Europe/Berlin"
	}
	responses = openmeteo.weather_api(url, params=params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")

	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
	hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
	hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
	hourly_wind_speed_100m = hourly.Variables(5).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
	hourly_data["precipitation"] = hourly_precipitation
	hourly_data["weather_code"] = hourly_weather_code
	hourly_data["cloud_cover"] = hourly_cloud_cover
	hourly_data["wind_speed_100m"] = hourly_wind_speed_100m

	df = pd.DataFrame(data = hourly_data)
	return df

@flow(name='ingest_Flow')
def call_main(): 
	parser = argparse.ArgumentParser(description='Ingest latest weather data to Postgres')
	parser.add_argument('--user', help ='user name for postgres')
	parser.add_argument('--password', help='password for postgres')
	parser.add_argument('--host', help='host for postgres')
	parser.add_argument('--port', help='port for postgres')
	parser.add_argument('--db', help='database name for postgres')
	parser.add_argument('--table_name', help='name of the table where we will write the results to')

	args = parser.parse_args()
	main(args)

if __name__ == '__main__':
	call_main()