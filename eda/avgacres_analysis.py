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

# Convert the seasonal decomposition result to a DataFrame for plotting with plotnine
avgacres_seasonal_df = pd.DataFrame({
    'year': average_acres_burned_per_year.index,
    'seasonal': aaDeco.seasonal,
    'trend': aaDeco.trend,
    'resid': aaDeco.resid
}).reset_index(drop=True)

avgacres_linreg_df = pd.DataFrame({
    'year': average_acres_burned_per_year.index,
    'avg_acres_year_trend': aaDeco.trend
}).reset_index(drop=True).dropna()


linreg1 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 1950) & (avgacres_linreg_df['year'] < 1960)].dropna()
linreg2 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 1960) & (avgacres_linreg_df['year'] <= 1970)].dropna()
# Perform linear regression
X = linreg1[['year']]
y = linreg1['avg_acres_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg1['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg1_plot = (ggplot(linreg1, aes(x='year', y='avg_acres_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='AvgAcres Trend for 1950-1960',
           x='Year',
           y='Trend (Acres Burned)')
    + annotate('text', x=1955, y=linreg1['avg_acres_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red'))

# Save the plot
#linreg1_plot.save('temp-plots/1950-1960.png')

linreg3 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 1970) & (avgacres_linreg_df['year'] <= 1980)].dropna()
linreg4 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 1980) & (avgacres_linreg_df['year'] <= 1990)].dropna()
linreg5 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 1990) & (avgacres_linreg_df['year'] <= 2000)].dropna()
linreg6 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 2010) & (avgacres_linreg_df['year'] <= 2020)].dropna()
linreg7 = avgacres_linreg_df[(avgacres_linreg_df['year'] >= 2020)].dropna()

print(linreg1)


linreg1_data = (ggplot(linreg1, aes(x='year', y='avg_acres_year_trend'))
    + geom_point()
    + labs(title='AvgAcres Trend for 1950-1960',
           x='Year',
           y='Trend (Acres Burned)'))



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
    + labs(title='Fire Acreage Trend, National Average',
           x='Year',
           y='Acreage (deasonalized-average)'))

# Plot the residual component
avgacres_resid_plot = (ggplot(avgacres_seasonal_df, aes(x='year', y='resid'))
    + geom_line()
    + labs(title='Residual Component of Average Acres Burned',
           x='Year',
           y='Avg Acres Burned'))

# Plot the average acres burned per year
avgacres_burned_vs_year_plot = (ggplot(average_acres_burned_per_year.reset_index(), aes(x='year', y='avg_acres_year'))
    + geom_line()
    + geom_point()
    + labs(title='Average Acres Burned Per Year',
           x='Year',
           y='Average Acres Burned'))



avgacres_trend_plot.save('results-gen/avgacres_trend.png')
#avgacres_resid_plot.save('results-gen/avgacres_residual.png')

