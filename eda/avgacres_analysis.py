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
data['acres_burned'] = pd.read_csv(data_path, usecols=['TOTALACRES'])
data['year'] = pd.read_csv(data_path, usecols=['FIREYEAR'])

#modify range
data = data[data['year'] > 1900]


# Calculate average acres burned per year, only for years where fires occurred
average_acres_burned_per_year = data[data['acres_burned'] > 0].groupby('year')['acres_burned'].mean().reset_index()
average_acres_burned_per_year.columns = ['year', 'avg_acres_year']
# Perform seasonal decomposition
# Perform seasonal decomposition by annual period on the average acres burned per year
average_acres_burned_per_year.set_index('year', inplace=True)
aaDeco = seasonal_decompose(average_acres_burned_per_year['avg_acres_year'], model='additive', period=12)

# Convert the seasonal decomposition result to a DataFrame for plotting with plotnine
avgacres_seasonal_df = pd.DataFrame({
    'year': average_acres_burned_per_year.index,
    'seasonal': aaDeco.seasonal,
    'trend': aaDeco.trend,
    'resid': aaDeco.resid
}).reset_index(drop=True)

# Print the trend component values for each year, dropping NaN values
avgacres_seasonal_df_printable = pd.DataFrame({
    'year': average_acres_burned_per_year.index,
    'trend': aaDeco.trend
}).dropna().reset_index(drop=True)


# Plot the seasonal component
avgacres_seasonal_plot = (ggplot(avgacres_seasonal_df, aes(x='year', y='seasonal'))
    + geom_line()
    + labs(title='Seasonal Component of Average Acres Burned',
           x='Year',
           y='Seasonal'))

# Plot the trend component
avgacres_trend_plot = (ggplot(avgacres_seasonal_df, aes(x='year', y='trend'))
    + geom_line()
    + labs(title='Trend Component of Average Acres Burned',
           x='Year',
           y='Avg Acres Burned'))

# Plot the residual component
avgacres_resid_plot = (ggplot(avgacres_seasonal_df, aes(x='year', y='resid'))
    + geom_line()
    + labs(title='Residual Component of Average Acres Burned',
           x='Year',
           y='Avg Acres Burned'))

# Save the plots
avgacres_seasonal_plot.save('results-gen/avgacres_seasonal.png')
avgacres_trend_plot.save('results-gen/avgacres_trend.png')
avgacres_resid_plot.save('results-gen/avgacres_residual.png')

