import pandas as pd
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs, annotate
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.linear_model import LinearRegression
from plotnine import geom_smooth
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
data = data[data['year'] > 1986]


# Calculate average acres burned per year, only for years where fires occurred
average_acres_burned_per_year = data[data['acres_burned'] > 0].groupby('year')['acres_burned'].mean().reset_index()
average_acres_burned_per_year.columns = ['year', 'avg_acres_year']
# Perform seasonal decomposition
# Perform seasonal decomposition by annual period on the average acres burned per year
average_acres_burned_per_year.set_index('year', inplace=True)
aaDeco = seasonal_decompose(average_acres_burned_per_year['avg_acres_year'], model='additive', period=12)


# Plot the average acres burned per year
avgacres_burned_vs_year_plot = (ggplot(average_acres_burned_per_year.reset_index(), aes(x='year', y='avg_acres_year'))
    + geom_line()
    + geom_point()
    + labs(title='Average Acres Burned Per Year',
           x='Year',
           y='Average Acres Burned'))

# Save the plot
avgacres_burned_vs_year_plot.save('results-gen/avgacres_burned_vs_year.png')

# Save the plots
avgacres_burned_vs_year_plot.save('results-gen/avgacres_burned_vs_year.png')
#avgacres_trend_plot.save('results-gen/avgacres_trend.png')
#avgacres_resid_plot.save('results-gen/avgacres_residual.png')

