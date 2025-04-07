from pathlib import Path
import pandas as pd
import pandas_gbq
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task(retries = 3)
def extract_from_gcs():
    """Download trip data from GCS"""
    gcs_path = f"data.parquet"
    local_path = f"data/"
    gcs_block = GcsBucket.load("gcs-connector")
    gcs_block.get_directory(from_path=gcs_path, local_path=local_path)
    return Path(f"{local_path}{gcs_path}")

@task()
def transform(path):
    """Data cleaning"""
    df = pd.read_parquet(path)
    print('placeholder for data transformation')
    return df

@task()
def write_BigQuery(df):
    """Write Dataframe"""
    gcp_credentials_block = GcpCredentials.load("gcp-creds")

    pandas_gbq.to_gbq(
        df, 
        destination_table = "weather_dataset_0.table0",
        project_id = "dataengineering-455510",
        credentials = gcp_credentials_block.get_credentials_from_service_account(),
        if_exists="append", 

    )
    


@flow()
def gcs_to_BigQuery():
    """Main ETL flow to load data into BigQuery"""
    path = extract_from_gcs()
    df = transform(path)
    write_BigQuery(df)

if __name__ == "__main__":
    gcs_to_BigQuery()