# weather_predictor
This project serves as the Capstone project for the Data Engineering Zoomcamp 2025. 

Problem:
Weather prediction is a non-trivial process, that is based on measuring various parameters and predicting their further propagation into neighouring regions using physical formulas. While this has proven reliable in the short term, predicting the weather for the next 1-3 days, the weather predictions beyond that still remain relatively unreliable. However modern AI tools have improved that situation. One especially useful tool is the Long Short Term Memory (LSTM) recurrent neural network. 
A prerequisite for using this tool for weather prediction is a well maintained and up to date database. 

Dataset creation and used technologies:
To create such a database for the city Wuppertal in Germany, I set up the following pipeline, starting from the website open-meteo.com, which offers a free API to download past weather data:

API -> local storage in Parquet
local storage in Parquet -> Datalake (Google Cloud Storage)
Datalake -> Datawarehouse (BigQuery)
Data transformation from and to BigQuery (dbt)
Data visualization (Google Looker Studio)

The pipelines are run in batch mode using Prefect, which is also used for Workflow Orchestration. 

Outlook:
In the future I will use this is as a basis to use LSTM for weather prediction. Additionally to use only the data for Wuppertal, I will then also add readouts from citys that are 200 km north, south, east and west of Wuppertal, which should substantially improve the performance of the LSTM in predicting the weather in Wuppertal. 
