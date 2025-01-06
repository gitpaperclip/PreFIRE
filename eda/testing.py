import pandas as pd
from plotnine import ggplot, aes, geom_point, geom_line, geom_path, labs
from statsmodels.tsa.arima.model import ARIMA

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
data['time_to_put_out'] = (data['end_time'] - data['start_time']).dt.total_seconds() / (24 * 3600)  # Convert to days
data = data[(data['time_to_put_out'] > 0) & (data['time_to_put_out'] <= 365)]
data['year'] = pd.read_csv(data_path, usecols=['FIREYEAR'])
data = data[data['year'] > 2010]


# Calculate average acres burned per year, only for years where fires occurred
average_acres_burned_per_year = data[data['acres_burned'] > 0].groupby('year')['acres_burned'].mean().reset_index()
average_acres_burned_per_year.columns = ['year', 'avg_acres_year']
average_acres_burned_df = average_acres_burned_per_year['avg_acres_year']
def average_adjacent_values(df, column):
    df['rolling_avg'] = df[column].rolling(window=2).mean()
    return df.dropna().reset_index(drop=True)

average_acres_burned_df = average_adjacent_values(average_acres_burned_per_year, 'avg_acres_year')



rolling_df = average_adjacent_values(average_acres_burned_per_year, "avg_acres_year")
rolling_acreavg = rolling_df["avg_acres_year"]
print(len(rolling_acreavg))
# Example usage:
average_acres_burned_df = average_adjacent_values(average_acres_burned_per_year, 'avg_acres_year')

# Calculate average time to put out per year
average_time_to_put_out_per_year = data[data['time_to_put_out'] > 0].groupby('year')['time_to_put_out'].mean().reset_index()
average_time_to_put_out_per_year.columns = ['year', 'avg_time_year']
average_time_out_df = average_time_to_put_out_per_year['avg_time_year']


# Merge the averages back into the original dataframe
data = pd.merge(data, average_acres_burned_per_year, on='year', how='left')
data = pd.merge(data, average_time_to_put_out_per_year, on='year', how='left')
#data = data[data['acres_burned'] < 1000]


acres_burned_vs_year = (ggplot(data, aes(x='year', y='acres_burned', color='year'))
    + geom_point()
    + labs(title='Year vs Acres Burned',
           x='year',
           y='acres burned'))


pathplot = (ggplot(data, aes(x='average_acres_burned_df', y='average_time_out_df', color='year'))
    + geom_path()
    + labs(title='Acres vs Time to Put out with year as color',
           x='Average Acres burned',
           y='Average time to put out'))

avgacres = (ggplot(data, aes(x='year', y='avg_acres_year', color='year'))
    + geom_line()
    + labs(title='Year vs Average Acres Burned',
           x='Year',
           y='Average Acres Burned'))

rollingacres  = (ggplot(data, aes(x='year', y='rolling_acreavg', color='year'))
    + geom_point()
    + labs(title='Year vs Average Acres Burned',
           x='Year',
           y='Average Acres Burned'))

avgtimeout = (ggplot(data, aes(x='year', y='avg_time_year', color='year'))
    + geom_line()
    + labs(title='Year vs Average Time To Put Out',
           x='Year',
           y='Average Time To Put Out'))



rollingacres.save('results-gen\\rolling.png')
# Save the new plots
#avgtimeout.save('results-gen\\average_time_to_put_out_plot.png')
# Save the plot
#pathplot.save('results-gen\\fire_plot.png')
#timeout_vs_year.save('results-gen\\fire_plot_2.png')
