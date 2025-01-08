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
data = data[data['year'] > 1900]

average_acres_burned_per_year = data[data['acres_burned'] > 0].groupby('year')['acres_burned'].mean().reset_index()
average_acres_burned_per_year.columns = ['year', 'avg_acres_year']

# Calculate average time to put out per year
average_time_to_put_out_per_year = data[data['time_to_put_out'] > 0].groupby('year')['time_to_put_out'].mean().reset_index()
average_time_to_put_out_per_year.columns = ['year', 'avg_time_year']

# Perform seasonal decomposition by annual period on the average acres burned per year
average_acres_burned_per_year.set_index('year', inplace=True)
aaDeco = seasonal_decompose(average_acres_burned_per_year['avg_acres_year'], model='additive', period=12)

# Perform seasonal decomposition by annual period on the average time to put out per year
average_time_to_put_out_per_year.set_index('year', inplace=True)
ttoDeco = seasonal_decompose(average_time_to_put_out_per_year['avg_time_year'], model='additive', period=12)


# Convert the seasonal decompositions results to a DataFrame for plotting with plotnine
seasonal_df = pd.DataFrame({
    'year': average_acres_burned_per_year.index,
    'aadeco': aaDeco.trend,
    'ttodeco': ttoDeco.trend,
}).reset_index(drop=True).dropna()


pathplot = (ggplot(seasonal_df, aes(x='aadeco', y='ttodeco', color='year'))
    + geom_path()
    + labs(title='Acres vs Time to Put out with year as color',
           x='Average Acres Burned trend', 
           y='Time to Put Out Fire Trend'))

pathplot.save('avg_pathplots\\trends.png')
# Save the new plots
#avgtimeout.save('results-gen\\average_time_to_put_out_plot.png')
# Save the plot
#pathplot.save('results-gen\\fire_plot.png')
#timeout_vs_year.save('results-gen\\fire_plot_2.png')
