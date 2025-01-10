import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import HeatMap
from shapely.geometry import Point
import geopandas as gpd

print(pd.__version__)

data_path = "resources\\usfs_data.csv"


location_data_lat_long = pd.read_csv(data_path, usecols=['LATDD83', 'LONGDD83', 'TOTALACRES', 'DISCOVERYDATETIME', 'FIREOUTDATETIME', 'FIREYEAR'])
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

latonly = df_cleaned['LATDD83'].dropna()
longonly = df_cleaned['LONGDD83'].dropna()

map_center = [37.0902, -95.7129]  # Approximate center of the US
us_map = folium.Map(location=map_center, zoom_start=5)

# Create a list of coordinates for the heatmap
heat_data = [[lat, lon] for lat, lon in zip(latonly, longonly)]



# Add the heatmap layer with custom range and opacity
HeatMap(
    heat_data,
    radius=1,           # Adjust radius for individual points
    blur=1,             # Control the amount of blur (smoothness)
    min_opacity=0,     # Adjust the lowest opacity for low intensity areas
).add_to(us_map)


# Add the heatmap layer to the map
weights = df_cleaned['TOTALACRES'].fillna(0)  # Handle NaNs in the acres burned column
HeatMap(list(zip(df_cleaned['LATDD83'], df_cleaned['LONGDD83'], weights)), radius=5, blur=5).add_to(us_map)



# Save the map to an HTML file
us_map.save('avg_pathplots\\wildfire_heatmap_us.html')

print(df_cleaned)