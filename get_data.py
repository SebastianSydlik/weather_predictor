#!/usr/bin/env python
# coding: utf-8
import argparse
import pandas as pd
import weather_API

from sqlalchemy import create_engine
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect.blocks.fields import SecretDict
from prefect_gcp.cloud_storage import GcsBucket
from pathlib import Path

@task(retries = 3)
def extract_data():
	df = weather_API.get_data_from_api()
	return df

@task(log_prints=True)
def transform_data(df):
	print(f'\npre: nan Count:\n{df.isnull().sum()}')
	df_clean = df.dropna()
	print(f'\npost: nan Count:\n{df_clean.isnull().sum()}')
	return df_clean

@task(log_prints=True)
def store_data(df, table_name):
	connection_block = SqlAlchemyConnector.load("postgres-connector")
	with connection_block.get_connection(begin=False) as engine: 
		print(df.to_sql(name=f'{table_name}', con=engine, if_exists='replace'))
		
@task()
def store_local(df):
	"""store dataframe locally as parquet file"""
	path = Path(f"data/data.parquet")
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
def etl_web_to_postgres(params):
	table_name = params.table_name

	df_raw = extract_data()
	df = transform_data(df_raw)
	path = store_local(df)
	store_data(df, table_name)
	write_gcs(path)
	
@flow(name='ingest_Flow')
def call_main(): 
	parser = argparse.ArgumentParser(description='Ingest latest weather data to Postgres')
	parser.add_argument('--table_name', help='name of the table where we will write the results to')

	args = parser.parse_args()
	etl_web_to_postgres(args)

if __name__ == '__main__':
	call_main()