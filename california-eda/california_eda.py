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

# Perform a spatial join to filter points within California. This is the USFS data ONLY for california!
df_cleaned = gpd.sjoin(geo_df, california, predicate='within')
