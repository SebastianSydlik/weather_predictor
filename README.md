# weather_predictor
In this project I create a pipeline that downloads various weather parameters of the last three months from open-meteo.com for Wuppertal in Germany. The data is stored in a DataLake on Google Cloud Storage and then transferred into a Datawarehouse in BigQuery. From there the data is transformed using dbt and two parameters (temperature over time and distribution of weather types) are then displayed in a dashboard using Google Looker Studio. 

This project serves as the Capstone project for the Data Engineering Zoomcamp 2025. In the future I will use this is as a basis to use LSTM for weather prediction.
