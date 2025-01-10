import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import HeatMap
from shapely.geometry import Point
import geopandas as gpd
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import time

print(pd.__version__)

data_path = "resources\\usfs_data.csv"


location_data_lat_long = pd.read_csv(data_path, usecols=['LATDD83', 'LONGDD83', 'TOTALACRES', 'DISCOVERYDATETIME', 'FIREOUTDATETIME', 'FIREYEAR']).dropna()
df_cleaned = location_data_lat_long.dropna(subset=['LATDD83', 'LONGDD83', 'TOTALACRES'])


# Load the shapefile or GeoJSON of California boundary
california = gpd.read_file('resources\\california.geojson')

# Create a GeoDataFrame from the dataframe
geometry = [Point(xy) for xy in zip(df_cleaned['LONGDD83'], df_cleaned['LATDD83'])]
geo_df = gpd.GeoDataFrame(df_cleaned, geometry=geometry, crs="EPSG:4326")

# Ensure both GeoDataFrames have the same CRS
geo_df = geo_df.to_crs(california.crs)

# Perform a spatial join to filter points within California
df_cleaned = gpd.sjoin(geo_df, california, predicate='within')

# Filter to only include fires after 2000 and greater than 10 acres
df_cleaned = df_cleaned[df_cleaned['FIREYEAR'] > 2015]
df_cleaned = df_cleaned[df_cleaned['TOTALACRES'] > 10].dropna()

# Ensure the DISCOVERYDATETIME column is in the correct format
df_cleaned['DISCOVERYDATETIME'] = pd.to_datetime(df_cleaned['DISCOVERYDATETIME']).dt.strftime('%Y-%m-%d')

print(df_cleaned['DISCOVERYDATETIME'])
    
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
weather_data_list = []
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"


print(df_cleaned.iloc[0])
print(df_cleaned.iloc[0]['DISCOVERYDATETIME'])
for index, row in df_cleaned.iterrows():
    params = {
        "latitude": row['LATDD83'],
        "longitude": row['LONGDD83'],
        "start_date": (pd.to_datetime(row['DISCOVERYDATETIME']).strftime('%Y-%m-%d')),
        "end_date": (pd.to_datetime(row['DISCOVERYDATETIME']) + pd.Timedelta(days=1)).strftime('%Y-%m-%d'),
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunshine_duration", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(2).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(3).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(5).ValuesAsNumpy()
    daily_wind_direction_10m_dominant = daily.Variables(6).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "temperature_2m_max": daily_temperature_2m_max,
        "temperature_2m_min": daily_temperature_2m_min,
        "sunshine_duration": daily_sunshine_duration,
        "precipitation_sum": daily_precipitation_sum,
        "wind_speed_10m_max": daily_wind_speed_10m_max,
        "wind_gusts_10m_max": daily_wind_gusts_10m_max,
        "wind_direction_10m_dominant": daily_wind_direction_10m_dominant,
        "latitude": row['LATDD83'],
        "longitude": row['LONGDD83']

    }
    
    daily_dataframe = pd.DataFrame(data=daily_data)
    weather_data_list.append(daily_dataframe)
    print(f"Successful API call for index {index}")
    time.sleep(1)

# Combine all dataframes into a single dataframe
all_weather_data = pd.concat(weather_data_list, ignore_index=True)
print(all_weather_data)

# Save the combined dataframe to a CSV file
all_weather_data.to_csv('results-gen\\california_100acre_fire_weather_data.csv', index=False)

# Combine all dataframes into a single dataframe
all_weather_data = pd.concat(weather_data_list, ignore_index=True)
print(all_weather_data)