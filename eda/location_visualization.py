import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import HeatMap

print(pd.__version__)

data_path = "resources\\usfs_data.csv"


location_data_lat_long = pd.read_csv(data_path, usecols=['LATDD83', 'LONGDD83', 'TOTALACRES', 'FIREYEAR'])
df_cleaned = location_data_lat_long.dropna(subset=['LATDD83', 'LONGDD83', 'TOTALACRES', 'FIREYEAR'])
df_cleaned = df_cleaned[df_cleaned['FIREYEAR'] > 2000]

latonly = df_cleaned['LATDD83']
longonly = df_cleaned['LONGDD83']

map_center = [37.0902, -95.7129]  # Approximate center of the US
us_map = folium.Map(location=map_center, zoom_start=5)

# Create a list of coordinates for the heatmap
heat_data = [[lat, lon] for lat, lon in zip(latonly, longonly)]



# Add the heatmap layer with custom range and opacity
HeatMap(
    heat_data,
    radius=8,           # Increase radius for better visibility
    blur=4,             # Adjust blur for smoothness
    min_opacity=0.2,    # Increase minimum opacity for better visibility of low intensity areas
    max_zoom=1,         # Adjust max zoom for better clarity
).add_to(us_map)


# Add the heatmap layer to the map
weights = df_cleaned['TOTALACRES'].fillna(0)  # Handle NaNs in the acres burned column
HeatMap(list(zip(df_cleaned['LATDD83'], df_cleaned['LONGDD83'], weights)), radius=5, blur=5).add_to(us_map)



# Save the map to an HTML file
us_map.save('results-gen\\wildfire_heatmap_us.html')
