import pandas as pd
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs, annotate, scale_x_continuous, xlim
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

tto_linreg_df = pd.DataFrame({
    'year': average_time_to_put_out_per_year.index,
    'tto_year_trend': ttoDeco.trend
}).reset_index(drop=True).dropna()


linreg1 = tto_linreg_df[(tto_linreg_df['year'] >= 1950) & (tto_linreg_df['year'] < 1960)].dropna()
linreg2 = tto_linreg_df[(tto_linreg_df['year'] >= 1960) & (tto_linreg_df['year'] < 1970)].dropna()
linreg3 = tto_linreg_df[(tto_linreg_df['year'] >= 1970) & (tto_linreg_df['year'] < 1980)].dropna()
linreg4 = tto_linreg_df[(tto_linreg_df['year'] >= 1980) & (tto_linreg_df['year'] < 1990)].dropna()
linreg5 = tto_linreg_df[(tto_linreg_df['year'] >= 1990) & (tto_linreg_df['year'] < 2000)].dropna()
linreg6 = tto_linreg_df[(tto_linreg_df['year'] >= 2000) & (tto_linreg_df['year'] < 2010)].dropna()
linreg7 = tto_linreg_df[(tto_linreg_df['year'] >= 2010) & (tto_linreg_df['year'] < 2025)].dropna()

### 1950-1960 Trend Regression
X = linreg1[['year']]
y = linreg1['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg1['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg1_plot = (ggplot(linreg1, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Avg Time to Put Out Fire Trend for 1950-1960',
           x='Year',
           y='Trend (Avg. Days To Put Out)')
    + annotate('text', x=1955, y=linreg1['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(1950, 1960))
    + xlim(1950, 1960))

# Save the plot
linreg1_plot.save('avgtto_trend_plots/avgtto_trend_1950-1960.png')

### 1960-1970 Trend Regression
X = linreg2[['year']]
y = linreg2['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg2['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg2_plot = (ggplot(linreg2, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Avg Time to Put Out Fire Trend for 1960-1970',
           x='Year',
           y='Trend (Days to Put Out Fire)')
    + annotate('text', x=1965, y=linreg2['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(1960, 1970))
    + xlim(1960, 1970))

# Save the plot
linreg2_plot.save('avgtto_trend_plots/avgtto_trend_1960-1970.png')

### 1970-1980 Trend Regression
X = linreg3[['year']]
y = linreg3['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg3['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg3_plot = (ggplot(linreg3, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Avg Time to Put Out Fire Trend for 1970-1980',
           x='Year',
           y='Trend (Days to Put Out Fire)')
    + annotate('text', x=1975, y=linreg3['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(1970, 1980))
    + xlim(1970, 1980))

# Save the plot
linreg3_plot.save('avgtto_trend_plots/avgtto_trend_1970-1980.png')

### 1980-1990 Trend Regression
X = linreg4[['year']]
y = linreg4['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg4['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg4_plot = (ggplot(linreg4, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Average Time to Put Out Fire Trend for 1980-1990',
           x='Year',
           y='Trend (Days to Put out fire)')
    + annotate('text', x=1985, y=linreg4['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(1980, 1990))
    + xlim(1980, 1990))

# Save the plot
linreg4_plot.save('avgtto_trend_plots/avgtto_trend_1980-1990.png')

### 1990-2000 Trend Regression
X = linreg5[['year']]
y = linreg5['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg5['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg5_plot = (ggplot(linreg5, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Avg Time to Put Out Fire for 1990-2000',
           x='Year',
           y='Trend (Days to Put Out Fire)')
    + annotate('text', x=1995, y=linreg5['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(1990, 2000))
    + xlim(1990, 2000))

# Save the plot
linreg5_plot.save('avgtto_trend_plots/avgtto_trend_1990-2000.png')

### 2000-2010 Trend Regression
X = linreg6[['year']]
y = linreg6['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg6['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg6_plot = (ggplot(linreg6, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Avg Time to Put Out Fire Trend for 2000-2010',
           x='Year',
           y='Trend (Days to Put Out Fire)')
    + annotate('text', x=2005, y=linreg6['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(2000, 2010))
    + xlim(2000, 2010))

# Save the plot
linreg6_plot.save('avgtto_trend_plots/avgtto_trend_2000-2010.png')


### 2010-2024 Trend Regression
X = linreg7[['year']]
y = linreg7['tto_year_trend']
reg = LinearRegression().fit(X, y)
slope = reg.coef_[0]
intercept = reg.intercept_

# Create the regression line
linreg7['regression_line'] = reg.predict(X)

# Plot with regression line and equation
linreg7_plot = (ggplot(linreg7, aes(x='year', y='tto_year_trend'))
    + geom_point()
    + geom_line(aes(y='regression_line'), color='blue')
    + labs(title='Avg Time to Put Out Fire Trend for 2010-2024',
           x='Year',
           y='Trend (Days to Put out Fire)')
    + annotate('text', x=2015, y=linreg7['tto_year_trend'].max(), 
               label=f'y = {slope:.2f}x + {intercept:.2f}', 
               ha='left', va='bottom', size=10, color='red')
    + scale_x_continuous(breaks=range(2010, 2025))
    + xlim(2010, 2025))

# Save the plot
linreg7_plot.save('avgtto_trend_plots/avgtto_trend_2010-2024.png')

