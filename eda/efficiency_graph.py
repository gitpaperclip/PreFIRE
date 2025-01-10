import pandas as pd
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
# Load the data
data_path = "resources\\usfs_data.csv"
data = pd.read_csv(data_path, usecols=['DISCOVERYDATETIME', 'FIREOUTDATETIME', 'TOTALACRES'])

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
data = data[data['year'] > 2000]

average_acres_burned_per_year = data[data['acres_burned'] > 0].groupby('year')['acres_burned'].mean().reset_index()
average_acres_burned_per_year.columns = ['year', 'avg_acres_year']

# Calculate average time to put out per year
average_time_to_put_out_per_year = data[data['time_to_put_out'] > 0].groupby('year')['time_to_put_out'].mean().reset_index()
average_time_to_put_out_per_year.columns = ['year', 'avg_time_year']
# Calculate efficiency as average time to put out divided by average acres burned per year

efficiency_df = pd.merge(average_time_to_put_out_per_year, average_acres_burned_per_year, on='year')
efficiency_df['efficiency'] = efficiency_df['avg_time_year'] / efficiency_df['avg_acres_year']

# Plot efficiency over the years
efficiency_plot = (ggplot(efficiency_df, aes(x='year', y='efficiency'))
    + geom_line()
    + labs(title='Efficiency of Firefighting Over the Years',
           x='Year', 
           y='Average Time to Put Out per Average Acres Burned'))

efficiency_plot.save('avg_pathplots\\efficiency_plot.png')

# Save the new plots
#avgtimeout.save('results-gen\\average_time_to_put_out_plot.png')
# Save the plot
#pathplot.save('results-gen\\fire_plot.png')
#timeout_vs_year.save('results-gen\\fire_plot_2.png')
