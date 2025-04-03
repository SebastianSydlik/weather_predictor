from pathlib import Path
import pandas as pd
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
def transform():
    """Data cleaning"""
    df = pd.read_parquet(path)
    print('placeholder for data transformation')
    return df

@task()
def write_BigQuery(df):
    """Write Dataframe"""
    gcp_creentials_block = GcpCredentials.load("")

    df.to_gbq(
        destination = ,
        project_id = ,
        credentials = gcp_credentials_block.get_credentials_from_service_account(),
        chunksize = 500000,
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