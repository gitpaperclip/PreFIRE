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
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs, annotate, scale_x_continuous, xlim


# Load the data
data_path = "resources\\usfs_data.csv"
data = pd.read_csv(data_path, usecols=['DISCOVERYDATETIME', 'FIREOUTDATETIME', 'TOTALACRES', 'LATDD83', 'LONGDD83'])

# Ensure the date columns are in datetime format
# Check for out-of-bounds datetime values
data = data[(data['DISCOVERYDATETIME'] != '9999-12-31') & (data['FIREOUTDATETIME'] != '9999-12-31')]
data['start_time'] = pd.to_datetime(data['DISCOVERYDATETIME'], errors='coerce')
data['end_time'] = pd.to_datetime(data['FIREOUTDATETIME'], errors='coerce')
data = data[data['end_time'] >= data['start_time']]
data['time_to_put_out'] = (data['end_time'] - data['start_time']).dt.total_seconds() / (24 * 3600)  # Convert to days
data = data[(data['time_to_put_out'] > 0) & (data['time_to_put_out'] <= 365)]
data['acres_burned'] = pd.read_csv(data_path, usecols=['TOTALACRES'])
data['year'] = pd.read_csv(data_path, usecols=['FIREYEAR'])
data = data[data['year'] > 1999]

# Load the shapefile or GeoJSON of California boundary
california = gpd.read_file('resources\\california.geojson')

# Create a GeoDataFrame from the dataframe
geometry = [Point(xy) for xy in zip(data['LONGDD83'], data['LATDD83'])]
geo_df = gpd.GeoDataFrame(data, geometry=geometry, crs="EPSG:4326")

# Ensure both GeoDataFrames have the same CRS
geo_df = geo_df.to_crs(california.crs)

# Perform a spatial join to filter points within California
data2 = gpd.sjoin(geo_df, california, predicate='within')
data2 = data[data['year'] > 2000]
data2 = data[data['acres_burned'] > 10].dropna()

average_acres_burned_per_year = data2[data2['acres_burned'] > 0].groupby('year')['acres_burned'].mean().reset_index()
average_acres_burned_per_year.columns = ['year', 'avg_acres_year']

# Calculate average time to put out per year
average_time_to_put_out_per_year = data2[data2['time_to_put_out'] > 0].groupby('year')['time_to_put_out'].mean().reset_index()
average_time_to_put_out_per_year.columns = ['year', 'avg_time_year']

efficiency_df = pd.merge(average_time_to_put_out_per_year, average_acres_burned_per_year, on='year')
efficiency_df['efficiency'] = efficiency_df['avg_time_year'] / efficiency_df['avg_acres_year']

# Perform seasonal decomposition by annual period on the average acres burned per year
efficiency_df.set_index('year', inplace=True)
eeDeco = seasonal_decompose(efficiency_df['efficiency'], model='additive', period=1)

# Convert the seasonal decompositions results to a DataFrame for plotting with plotnine
seasonal_df = pd.DataFrame({
    'year': efficiency_df.index,
    'eeDeco': eeDeco.trend
}).reset_index(drop=True).dropna()


pathplot = (ggplot(seasonal_df, aes(x='year', y='eeDeco'))
    + geom_path()
    + labs(title='Acreage vs Suppression Time, California',
           x='Year', 
           y='Average Time to Put Out (days, deseasonalized-trend)')
    + scale_x_continuous(breaks=range(int(seasonal_df['year'].min()), int(seasonal_df['year'].max()) + 1)))

# Save the new plots
#avgtimeout.save('results-gen\\average_time_to_put_out_plot.png')
# Save the plot
pathplot.save('avg_pathplots\\calif_efficiency_trend.png')
#timeout_vs_year.save('results-gen\\fire_plot_2.png')
