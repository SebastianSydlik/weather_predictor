import pandas as pd
import openmeteo_requests
import requests_cache

from retry_requests import retry
from datetime import date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

def get_data_from_api(location:dict) -> pd.DataFrame:
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)
	
	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://archive-api.open-meteo.com/v1/archive"

	print(location.get('latitude'))
	params = {
		"latitude": location.get("latitude"),
		"longitude": location.get("longitude"),
		"start_date": date.today() - relativedelta(months=3),
		"end_date": date.today(),
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

if __name__ == "__main__":
	print(get_data_from_api())