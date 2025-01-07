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
data['year'] = pd.read_csv(data_path, usecols=['FIREYEAR'])
data = data[data['year'] > 1900]


# Calculate average time to put out per year
average_time_to_put_out_per_year = data[data['time_to_put_out'] > 0].groupby('year')['time_to_put_out'].mean().reset_index()
average_time_to_put_out_per_year.columns = ['year', 'avg_time_year']

# Perform seasonal decomposition
# Perform seasonal decomposition by annual period on the average time to put out per year
average_time_to_put_out_per_year.set_index('year', inplace=True)
ttoDeco = seasonal_decompose(average_time_to_put_out_per_year['avg_time_year'], model='additive', period=12)

# Convert the seasonal decomposition result to a DataFrame for plotting with plotnine
tto_seasonal_df = pd.DataFrame({
    'year': average_time_to_put_out_per_year.index,
    'seasonal': ttoDeco.seasonal,
    'trend': ttoDeco.trend,
    'resid': ttoDeco.resid
}).reset_index(drop=True)

tto_seasonal_df_printable = pd.DataFrame({
    'year': average_time_to_put_out_per_year.index,
    'trend': ttoDeco.trend
}).dropna().reset_index(drop=True)


# Plot the seasonal component
tto_seasonal_plot = (ggplot(tto_seasonal_df, aes(x='year', y='seasonal'))
    + geom_line()
    + labs(title='Seasonal Component of Average FireOut Time',
           x='Year',
           y='Seasonal'))

# Plot the trend component
tto_trend_plot = (ggplot(tto_seasonal_df, aes(x='year', y='trend'))
    + geom_line()
    + labs(title='Trend Component of Average FireOut Time',
           x='Year',
           y='Avg. Fire Out Time (days)'))

# Plot the residual component
tto_resid_plot = (ggplot(tto_seasonal_df, aes(x='year', y='resid'))
    + geom_line()
    + labs(title='Residual Component of Average FireOut Time',
           x='Year',
           y='Avg. Fire Out Time (days)'))

# Save the plots
#tto_seasonal_plot.save('results-gen/tto_seasonal.png')
#tto_trend_plot.save('results-gen/tto_trend.png')
#tto_resid_plot.save('results-gen/tto_residual.png')


