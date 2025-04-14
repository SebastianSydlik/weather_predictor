# 🌦️ Weather Predictor

This repository contains the **Capstone Project** for the **Data Engineering Zoomcamp 2025**.

## 🧩 Problem Statement

Weather prediction is a complex and non-trivial task. Traditional methods rely on physical models that calculate how atmospheric conditions propagate into neighboring regions. These models are generally reliable for **short-term forecasts** (1–3 days), but accuracy significantly decreases for longer timeframes.

Recent advances in **Artificial Intelligence**, especially **Recurrent Neural Networks (RNNs)** like **Long Short-Term Memory (LSTM)** networks, have shown promise in extending the reliability of weather forecasting. However, using such models effectively requires a **clean, well-maintained, and up-to-date database** of historical weather data.

## 🛠️ Dataset Creation & Technologies Used

This project focuses on creating such a dataset and setting up the corresponding **data pipeline** for the city of **Wuppertal, Germany**. Weather data is sourced from [Open-Meteo](https://open-meteo.com/), which provides a **free API** for historical weather data.

### Pipeline Overview:

```text
API (Open-Meteo) 
   ↓ 
Local Storage (Parquet files) 
   ↓ 
Datalake (Google Cloud Storage) 
   ↓ 
Data Warehouse (BigQuery) 
   ↓ 
Data Transformations (dbt) 
   ↓ 
Data Visualization (Google Looker Studio)

```
### Tools
Prefect is used to orchestrate batch processing workflows.

Google Cloud Platform handles scalable data storage and transformation.

dbt (data build tool) enables modular and testable SQL transformations.

Looker Studio is used to create insightful visualizations of the collected data (see 'Screenshot Google Looker Studio.png', please message me for a direct access link).

Pipenv is used to create a virtual environment.

Prefect and the local database (PostgreSQL with PGAdmin) are run using docker compose.

## Outlook

The next step of the project involves training an LSTM model using this curated dataset to predict future weather in Wuppertal.

To enhance the model’s performance, I plan to incorporate data from cities approximately 200 km north, south, east, and west of Wuppertal. This spatial context should provide the LSTM with better insights into weather systems moving into the region, thereby improving forecast accuracy.
